import ipaddress
import json

import valkey
from loguru import logger

from .settings import config

vk_pool = valkey.ConnectionPool.from_url(str(config.valkey_url))
gimme_vk = lambda: valkey.Valkey(connection_pool=vk_pool, decode_responses=True)

SECONDS_IN_DAY = 60*60*24

def cut_ip(ip, trailing_bits):
    nm = (int(ip) >> trailing_bits) << trailing_bits
    return type(ip)(nm)
