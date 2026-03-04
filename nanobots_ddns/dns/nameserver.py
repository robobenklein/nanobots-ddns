import dnslib
from loguru import logger
from nserver import (
    NameServer, Query, Response,
    A, AAAA,
)
from nserver.application import DirectApplication
from nserver.transport import UDPv4Transport

from .settings import config
from ..util import gimme_vk, try_decode

server = NameServer("example")

#
# AttributeError: 'NameServer' object has no attribute 'register_raw_exception_handler'. Did you mean: 'register_exception_handler'?
#
#@server.exception_handler(Exception)
#def print_errors(exception: Exception, query: Query) -> Response:
#    logger.error(f"failed to process {record} due to {exception!r}")
#    response = record.reply()
#    response.header.rcode = dnslib.RCODE.SERVFAIL
#    return response

# upstream needs a fix
def dumbo_error_log(f):
    def wrap(*a, **kwa):
        try:
            return f(*a, **kwa)
        except Exception as e:
            logger.error(f"{e!r}")
    return wrap

@server.rule(f"*.v4.{config.tld}", ["A"])
@dumbo_error_log
def v4_records(query: Query):
    logger.debug(query)
    vk_key = f"v4/A/{query.name}"
    logger.debug(f"will fetch {vk_key}")
    vk = gimme_vk()
    r = try_decode(vk.get(vk_key))
    logger.debug(f"result {r}")
    return A(query.name, r)

@server.rule(f"*.v6.{config.tld}", ["AAAA"])
@dumbo_error_log
def v6_records(query: Query):
    logger.debug(query)
    vk_key = f"v6/AAAA/{query.name}"
    logger.debug(f"will fetch {vk_key}")
    vk = gimme_vk()
    r = try_decode(vk.get(vk_key))
    logger.debug(f"result {r}")
    return AAAA(query.name, r)


def run():
    logger.info(config)
    app = DirectApplication(server, UDPv4Transport(
        address=str(config.listen_addr),
        port=config.listen_port,
    ))
    logger.info(f"start {app}")
    app.run()
