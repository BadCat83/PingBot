from pydantic import BaseSettings, SecretStr, BaseModel
from ipaddress import IPv4Address

BLOCKING_TIME = 5


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = 'Config/.env'
        env_file_encoding = 'utf-8'


class User(BaseModel):
    user_id: str
    nick: str
    user_name: str
    is_administrator: bool


class Resource(BaseModel):
    resource_name: str
    domain_name: str
    ip_address: IPv4Address
