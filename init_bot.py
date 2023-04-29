from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from redis import Redis

from Config.config import Settings
import DB.sqlite as db

storage = MemoryStorage()
resources_storage = Redis(host='localhost', port=6379, decode_responses=True)
config = Settings()

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
