
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


if __name__ == '__main__':
    """allowed_users = {
        952969226: {'nick': 'bad_cat11', 'user_name': 'Nekhoroshev Konstantin'},
    }
    resource_list = {
        'Mikrotik': '92.119.216.1',
        'Bitrix': '92.119.216.3',
        'Checkpoint': '92.119.216.10',
        'Cisco_Gate': '92.119.216.15',
    }"""
    external_data = {
        'id': 952969226,
        'nick': 'bad_cat11',
        'user_name': 'Nekhoroshev Konstantin',
    }
    user = User(**external_data)
    print(user)
