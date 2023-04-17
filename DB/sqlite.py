import sqlite3 as sq

from aiogram.utils import json

from Config.config import User, Resource


async def db_start() -> None:
    global db, cur

    db = sq.connect('data.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY, nick TEXT, user_name TEXT, "
                "is_administrator BOOLEAN)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS resources(ip_address TEXT PRIMARY KEY, resource_name TEXT, describe TEXT,"
        " users_list TEXT)")
    db.commit()


async def check_users_exist() -> list:
    return cur.execute("SELECT * FROM users").fetchall()


# async def get_users(resource_ip=None) -> list:
#     if not resource_ip:
#         return cur.execute("SELECT users_id FROM resources")


async def check_user(user_id: str) -> list:
    return cur.execute("SELECT is_administrator FROM users WHERE user_id = ?", (user_id,)).fetchone()


async def get_resources() -> list:
    return cur.execute("SELECT * FROM resources").fetchall()


async def get_resources_ip() -> list:
    return cur.execute("SELECT ip_address FROM resources").fetchall()


async def get_resource_by_ip(ip: str) -> list:
    return cur.execute("SELECT resource_name FROM resources WHERE ip_address = ?", (ip,)).fetchone()[0]


async def get_resource_users(resource_ip: str) -> list:
    return json.loads(cur.execute("SELECT users_list FROM resources"
                                  " WHERE ip_address = ?", (resource_ip,)).fetchone()[0])


async def create_user(new_user: User) -> sq.Cursor:
    # user = cur.execute(f"SELECT 1 FROM users WHERE user_id == {user_id}").fetchone()
    # if not user:
    user = cur.execute("INSERT INTO users VALUES(?, ?, ?, ?)",
                       (new_user.user_id, new_user.nick, new_user.user_name, new_user.is_administrator))
    db.commit()
    return user


async def create_resource(new_resource: Resource) -> sq.Cursor:
    resource = cur.execute("INSERT INTO resources VALUES (?, ?, ?, ?)", (str(new_resource.ip_address),
                                                                         new_resource.resource_name,
                                                                         new_resource.describe,
                                                                         json.dumps(new_resource.users_id)))
    db.commit()
    return resource


async def add_users_to_res(users_id: list, ip_address: str) -> None:
    cur.execute("UPDATE resources SET users_list = ? WHERE ip_address = ?", (json.dumps(users_id), ip_address))
    db.commit()


async def edit_resources(state, resource_name) -> None:
    async with state.proxy() as data:
        cur.execute(f"UPDATE resources SET resource_name = '{data['resource_name']}',"
                    f"ip_address = '{data['ip_address']}',"
                    f"domain_name = '{data['domain_name']}'"
                    f"WHERE resource_name == {resource_name}")
        db.commit()


async def get_admin() -> list:
    return cur.execute("SELECT user_id FROM users WHERE is_administrator == 1").fetchall()
