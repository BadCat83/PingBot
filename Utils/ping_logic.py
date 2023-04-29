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
    res_list = {resource: {'avail': 1, 'dt': ' ', 'cnt': 0} for resource in resources_storage.lrange('res', 0, -1)}
    for key, val in res_list.items():
        resources_storage.hmset(key, val)
    dt = None
    while True:
        for ip in res_list:
            if (resources_storage.hget(ip, 'dt') != ' ') and not dt:
                dt = datetime.fromtimestamp(int(resources_storage.hget(ip, 'dt')))
            if resources_storage.hget(ip, 'avail') != '0':
                try:
                    delay = await aioping.ping(ip, timeout=5) * 1000
                    resources_storage.hset(ip, 'cnt', 0)
                    # print(f'{ip}:{delay}')
                except TimeoutError:
                    resources_storage.hset(ip, 'cnt', int(resources_storage.hget(ip, 'cnt')) + 1)
                    if int(resources_storage.hget(ip, 'cnt')) > 1:
                        resources_storage.hset(ip, 'dt', int(datetime.now().timestamp()))
                        resources_storage.hset(ip, 'avail', 0)
                        await send_message_to_users(ip, 'недоступен')
            elif (datetime.now() - datetime.fromtimestamp(int(resources_storage.hget(ip, 'dt')))) > timedelta(minutes=1):
                await send_message_to_users(ip, 'все еще недоступен')
                resources_storage.hset(ip, 'dt', int(datetime.now().timestamp()))
            else:
                try:
                    await aioping.ping(ip) * 1000
                except TimeoutError:
                    continue
                else:
                    delta = datetime.now() - dt
                    hours, minutes, seconds = time_format(delta)
                    await send_message_to_users(ip, f'доступен. Ресурс был недоступен - '
                                                    f'{hours}h:{minutes}m:{seconds}s')
                    resources_storage.hset(ip, 'avail', 1)
                    resources_storage.hset(ip, 'cnt', 0)
                    resources_storage.hset(ip, 'dt', ' ')
                    dt = None

        await asyncio.sleep(PING_TIMEOUT)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(do_ping("google.com"))
