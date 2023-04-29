import asyncio
from datetime import datetime, timedelta

import aioping

from Config.config import TIMEOUT, PING_TIMEOUT
from Utils.formating import time_format
from init_bot import db, dp, resources_storage


async def send_message_to_users(resource_ip: str, text: str) -> None:
    users = await db.get_resource_users(resource_ip)
    res_name = await db.get_resource_by_ip(resource_ip)
    for user in users:
        await dp.bot.send_message(user, f"Ресурс <b>{res_name}</b> {text}", parse_mode='HTML')


async def do_ping() -> None:
    await asyncio.sleep(TIMEOUT)
    resources = await db.get_resources_ip()
    resources_storage.flushdb()
    _ = [resources_storage.lpush('res', resource[0]) for resource in resources]

    while True:
        available = {resource: [True, None, 0] for resource in resources_storage.lrange('res', 0, -1)}
        for ip, param in available.items():
            if param[0]:
                try:
                    delay = await aioping.ping(ip, timeout=5) * 1000
                    available[ip][2] = 0
                    print(f'{ip}:{delay}')
                except TimeoutError:
                    available[ip][2] += 1
                    print(available[ip][2])
                    if available[ip][2] > 2:
                        available[ip][1] = datetime.now()
                        available[ip][0] = False
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
                    available[ip][2] = 0

        await asyncio.sleep(PING_TIMEOUT)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(do_ping("google.com"))
