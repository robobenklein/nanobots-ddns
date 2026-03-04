import ipaddress

import bottle
import valkey
from limits import storage, strategies, parse

from .util import cut_ip

limits_storage = storage.MemoryStorage()
limiter = strategies.SlidingWindowCounterRateLimiter(limits_storage)

def limited_ip(ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str]):
    if isinstance(ip, str):
        ip = ipaddress.ip_address(ip)
    match type(ip):
        case ipaddress.IPv4Address:
            return ip
        case ipaddress.IPv6Address:
            return cut_ip(ip, 64)
        case _:
            raise NotImplementedError()

# TODO a bottle plugin to handle the global rate limiting by limited_ip

# TODO a bottle plugin to handle per-route limits by uuid
