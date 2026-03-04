from nserver import (
    NameServer, Query, A, AAAA,
    DirectApplication, UDPv4Transport,
)

from .settings import config

server = NameServer("example")

@server.rule("example.com", ["A"])
def example_a_records(query: Query):
    return A(query.name, "1.2.3.4")


def run():
    app = DirectApplication(server, UDPv4Transport(
        address=config.listen_addr,
        port=config.listen_port,
    ))
    app.run()
