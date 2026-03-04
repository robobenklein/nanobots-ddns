from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    RedisDsn,
    networks,
)
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    listen_addr: networks.IPvAnyAddress = "127.0.0.1"
    listen_port: int = 1998
    valkey_url: RedisDsn = "redis://"
    debug: bool = True
    reloader: bool = True
    tld: str


config = Settings()
