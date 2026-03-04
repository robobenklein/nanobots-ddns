from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    RedisDsn,
    networks,
)
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from ..util import SharedSettings

load_dotenv()


class Settings(SharedSettings):
    listen_addr: networks.IPvAnyAddress = "127.0.0.1"
    listen_port: int = 53053


config = Settings()
