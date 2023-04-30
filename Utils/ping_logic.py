import asyncio
from datetime import datetime, timedelta

import aioping

from Config.config import TIMEOUT, PING_TIMEOUT
from Utils.formating import time_format
from init_bot import db, dp, resources_storage

"""This part of code launches as a separate flow and uses redis as a storage for keeping some variables that needed
at some logic. I'm new in Redis so I used it to the extent that I understood its work"""


async def send_message_to_users(resource_ip: str, text: str) -> None:
    """This function just sends a message to the user, informing them about the resource status"""
    users = await db.get_resource_users(resource_ip)
    res_name = await db.get_resource_by_ip(resource_ip)
    for user in users:
        await dp.bot.send_message(user, f"Ресурс <b>{res_name}</b> {text}", parse_mode='HTML')


async def do_ping() -> None:
    """The main logic of the ping function. Pings all the resources that is read from the database.
     Then, if one of them has become unavailable, sends the warning message to the subscribed users."""
    # Waiting while the database is initialized
    await asyncio.sleep(TIMEOUT)
    resources = await db.get_resources_ip()
    # I know that in this case the Redis losts its advantages, but in this logic it's not necessary
    # I just wanted to try this technology and have some practice in it
    resources_storage.flushdb()
    # Adding all the resources in Redis database as LIST
    _ = [resources_storage.lpush('res', resource[0]) for resource in resources]
    # Adding some parameters to keep track of the state of the resource
    for key, val in {resource: {
            'avail': 1,
            'dt': ' ',
            'cnt': 0
        } for resource in resources_storage.lrange('res', 0, -1)
    }.items():
        resources_storage.hmset(key, val)
    # Time tag to keep track when the resource became to be unavailable
    dt = None
    while True:
        # Getting resource list from Redis to have the ability to add resources in online mode
        for ip in resources_storage.lrange('res', 0, -1):
            if (resources_storage.hget(ip, 'dt') != ' ') and not dt:
                dt = datetime.fromtimestamp(int(resources_storage.hget(ip, 'dt')))
            if resources_storage.hget(ip, 'avail') != '0':
                try:
                    delay = await aioping.ping(ip, timeout=5) * 1000
                    resources_storage.hset(ip, 'cnt', 0)
                    # print(f'{ip}:{delay}')
                except TimeoutError:
                    resources_storage.hset(ip, 'cnt', int(resources_storage.hget(ip, 'cnt')) + 1)
                    # If there was little packet loss, don't spam the users with the messages
                    if int(resources_storage.hget(ip, 'cnt')) > 2:
                        resources_storage.hset(ip, 'dt', int(datetime.now().timestamp()))
                        resources_storage.hset(ip, 'avail', 0)
                        await send_message_to_users(ip, 'недоступен')
            # To don't spam users with the messages, if resource is unavailable, waiting for 15 minutes and
            # sending the message again
            elif (datetime.now() - datetime.fromtimestamp(int(resources_storage.hget(ip, 'dt')))) > timedelta(
                    minutes=15):
                await send_message_to_users(ip, 'все еще недоступен')
                resources_storage.hset(ip, 'dt', int(datetime.now().timestamp()))
            # If the resource becomes available, sending an appropriate message and turns into normal ping mode
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
