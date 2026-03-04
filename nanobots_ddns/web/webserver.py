#!/usr/bin/env python3
import os
import ipaddress
import json
from pathlib import Path
from typing import List, Optional, Dict

import bottle
import dns.rdata
import valkey
from pydantic import BaseModel, field_validator, model_validator
from loguru import logger

from .settings import config
from ..util import gimme_vk, SECONDS_IN_DAY
from .ratelimit import limited_ip
from .. import security

app = bottle.Bottle()


def simple_response(code=200, content: Optional[Union[dict, str]] = None):
    headers = {}
    body = None
    if type(content) == str:
        body = content
        headers["Content-Type"] = "text/plain"
    if type(content) == dict:
        body = json.dumps(content)
        headers["Content-Type"] = "application/json"
    return bottle.HTTPResponse(
        body=body,
        status=code,
        headers=headers,
    )


def get_client_ip():
    # TODO should be something like a TRUSTED_PROXIES list later?
    remote_addr = ipaddress.ip_address(bottle.request.remote_addr)
    logger.debug(f"bottle remote_addr {remote_addr}")
    if remote_addr.is_global:
        return remote_addr
    # TODO other cases to consider


@app.post("/v4/<key>")
def update_v4(key: str):
    record_uuid = security.key_to_uuid(key)
    logger.info(f"processing v4 request for {record_uuid}")
    r_ip = get_client_ip()
    logger.info(f"from {r_ip}")
    if not isinstance(r_ip, ipaddress.IPv4Address):
        return simple_response(
            400, f"v4 request must come from v4 IP address, you are {r_ip}"
        )
    r_ip = str(r_ip)
    fqdn = f"{record_uuid}.v4.{config.tld}"
    vk_key = f"v4/A/{fqdn}"
    vk = gimme_vk()
    old_value = vk.set(
        vk_key,
        r_ip,
        get=True,
        ex=7*SECONDS_IN_DAY,
    )
    if old_value:
        old_value = old_value.decode()
    if old_value == r_ip:
        return simple_response(204)
    return simple_response(
        201 if not old_value else 200, {
            "now": {fqdn: r_ip},
            "old": {fqdn: old_value},
        }
    )

@app.post("/v6/<key>")
def update_v6(key: str):
    record_uuid = security.key_to_uuid(key)
    logger.info(f"processing v6 request for {record_uuid}")
    r_ip = get_client_ip()
    logger.info(f"from {r_ip}")
    if not isinstance(r_ip, ipaddress.IPv6Address):
        return simple_response(
            400, f"v6 request must come from v6 IP address, you are {r_ip}"
        )
    r_ip = str(r_ip)
    fqdn = f"{record_uuid}.v6.{config.tld}"
    vk_key = f"v6/AAAA/{fqdn}"
    vk = gimme_vk()
    old_value = vk.set(
        vk_key,
        r_ip,
        get=True,
        ex=7*SECONDS_IN_DAY,
    )
    if old_value:
        old_value = old_value.decode()
    if old_value == r_ip:
        return simple_response(204)
    return simple_response(
        201 if not old_value else 200, {
            "now": {fqdn: r_ip},
            "old": {fqdn: old_value},
        }
    )


def run():
    """
    Run API webserver
    """
    gimme_vk().ping()
    app.run(
        host=str(config.listen_addr),
        port=config.listen_port,
        debug=config.debug,
        reloader=config.reloader,
    )
