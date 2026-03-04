import os
import uuid
from base64 import b64encode, b64decode

from loguru import logger
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import bcrypt

# must be 16 bytes
salt: bytes = b64decode(os.environ["NANOBOTS_SALT"])
assert len(salt) == 16


def key_to_uuid(key: str):
    bkey = key.encode("utf-8")
    b64key = b64encode(SHA256.new(bkey).digest())
    bc_hash = bcrypt(b64key, cost=12, salt=salt)
    # logger.debug(f"bc_hash {bc_hash}")
    uuid_bytes = SHA256.new(bc_hash).digest()[:16]
    return uuid.UUID(bytes=uuid_bytes)


if __name__ == "__main__":
    logger.info(key_to_uuid("TotallyRandomString"))
