import asyncio
from datetime import datetime, timedelta

import aioping

from Config.config import TIMEOUT
from Utils.formating import time_format
from init_bot import db, dp


async def send_message_to_users(resource_ip: str, text: str) -> None:
    users = await db.get_resource_users(resource_ip)
    res_name = await db.get_resource_by_ip(resource_ip)
    for user in users:
        await dp.bot.send_message(user, f"Ресурс <b>{res_name}</b> {text}", parse_mode='HTML')


async def do_ping() -> None:
    await asyncio.sleep(TIMEOUT)
    resources = await db.get_resources_ip()
    available = {resource[0]: [True, None] for resource in resources}
    while True:
        for ip, param in available.items():
            if param[0]:
                try:
                    await aioping.ping(ip) * 1000
                    # await asyncio.sleep(1)
                except TimeoutError:
                    available[ip][0] = False
                    available[ip][1] = datetime.now()
                    await send_message_to_users(ip, 'недоступен')
            elif (datetime.now() - available[ip][1]) > timedelta(minutes=15):
                available[ip][0] = True
            else:
                try:
                    await aioping.ping(ip) * 1000
                except TimeoutError:
                    continue
                else:
                    delta = datetime.now() - available[ip][1]
                    hours, minutes, seconds = time_format(delta)
                    await send_message_to_users(ip, f'доступен. Ресурс был недоступен - '
                                                    f'{hours}h:{minutes}m:{seconds}s')
                    available[ip][0] = True

        await asyncio.sleep(TIMEOUT)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(do_ping("google.com"))
