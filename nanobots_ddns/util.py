import ipaddress
import json

import valkey
from pydantic import (
    RedisDsn,
)
from pydantic_settings import BaseSettings
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

class SharedSettings(BaseSettings):
    valkey_url: RedisDsn = "redis://localhost/0"
    tld: str

config = SharedSettings()

vk_pool = valkey.ConnectionPool.from_url(str(config.valkey_url))
gimme_vk = lambda: valkey.Valkey(connection_pool=vk_pool, decode_responses=True)

SECONDS_IN_DAY = 60*60*24

def cut_ip(ip, trailing_bits):
    nm = (int(ip) >> trailing_bits) << trailing_bits
    return type(ip)(nm)

def try_decode(r):
    try:
        return r.decode()
    except:
        return r
