from pydantic import BaseSettings, SecretStr, BaseModel
from ipaddress import IPv4Address

"""Config file"""

BLOCKING_TIME = 1
TIMEOUT = 10
PING_TIMEOUT = 1


class Settings(BaseSettings):
    """It's needed for export bot token from env file"""
    bot_token: SecretStr

    class Config:
        env_file = 'Config/.env'
        env_file_encoding = 'utf-8'


class User(BaseModel):
    """Describes user"""
    user_id: str
    nick: str
    user_name: str
    is_administrator: bool


class Resource(BaseModel):
    """Describes resource"""
    resource_name: str
    ip_address: IPv4Address
    users_id: list
    describe: str
