import uuid
import json
import traceback

import dnslib
from loguru import logger
from nserver import (
    NameServer,
    Query,
    Response,
    A,
    AAAA,
)
from nserver.application import DirectApplication
from nserver.transport import UDPv4Transport

from .settings import config
from ..util import gimme_vk, try_decode

server = NameServer("example")

#
# AttributeError: 'NameServer' object has no attribute 'register_raw_exception_handler'. Did you mean: 'register_exception_handler'?
#
# @server.exception_handler(Exception)
# def print_errors(exception: Exception, query: Query) -> Response:
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
            logger.exception(e)

    return wrap


### v4 v6 ds
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


@server.rule(f"*.ds.{config.tld}", ["A", "AAAA"])
@dumbo_error_log
def ds_records(query: Query):
    logger.debug(query)
    parts = query.name.split(".")
    assert parts[1] == "ds"
    sub_uuid = uuid.UUID(parts[0])
    getit = lambda vk_key: try_decode(gimme_vk().get(vk_key))
    match query.type:
        case "A":
            return A(query.name, getit(f"v4/A/{sub_uuid}.v4.{config.tld}"))
        case "AAAA":
            return AAAA(query.name, getit(f"v6/AAAA/{sub_uuid}.v6.{config.tld}"))
        case _:
            raise NotImplementedError(
                f"cannot serve qtype {query.type} for {query.name}"
            )


### v4m v6m m
@server.rule(f"*.v4m.{config.tld}", ["A"])
@dumbo_error_log
def v4m_records(query: Query):
    logger.debug(query)
    vk_key = f"v4m/A/{query.name}"
    logger.debug(f"will fetch {vk_key}")
    vk = gimme_vk()
    r = try_decode(vk.get(vk_key))
    if not r:
        logger.debug(f"result not found")
        return []
    r = json.loads(r)
    logger.debug(f"result {r}")
    return list([A(query.name, ip) for ip in r])


@server.rule(f"*.v6m.{config.tld}", ["AAAA"])
@dumbo_error_log
def v6m_records(query: Query):
    logger.debug(query)
    vk_key = f"v6m/AAAA/{query.name}"
    logger.debug(f"will fetch {vk_key}")
    vk = gimme_vk()
    r = try_decode(vk.get(vk_key))
    if not r:
        logger.debug(f"result not found")
        return []
    r = json.loads(r)
    logger.debug(f"result {r}")
    return list([AAAA(query.name, ip) for ip in r])


@server.rule(f"*.m.{config.tld}", ["A", "AAAA"])
@dumbo_error_log
def m_records(query: Query):
    logger.debug(query)
    parts = query.name.split(".")
    assert parts[1] == "m"
    sub_uuid = uuid.UUID(parts[0])
    getit = lambda vk_key: try_decode(gimme_vk().get(vk_key))
    match query.type:
        case "A":
            RecordType = A
            ips = getit(f"v4m/A/{sub_uuid}.v4m.{config.tld}")
        case "AAAA":
            RecordType = AAAA
            ips = getit(f"v6m/AAAA/{sub_uuid}.v6m.{config.tld}")
        case _:
            raise NotImplementedError(
                f"cannot serve qtype {query.type} for {query.name}"
            )
    if ips:
        ips = json.loads(ips)
    else:
        logger.debug(f"no such record found for type m")
        return []
    return [RecordType(query.name, ip) for ip in ips]


def run():
    logger.info(config)
    app = DirectApplication(
        server,
        UDPv4Transport(
            address=str(config.listen_addr),
            port=config.listen_port,
        ),
    )
    logger.info(f"start {app}")
    app.run()
