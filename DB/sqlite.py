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
        "CREATE TABLE IF NOT EXISTS resources(ip_address TEXT PRIMARY KEY, resource_name TEXT, domain_name TEXT,"
        " users_id TEXT, describe TEXT)")
    db.commit()


async def check_users_exist() -> list:
    return cur.execute("SELECT * FROM users").fetchall()


async def create_user(new_user: User) -> sq.Cursor:
    # user = cur.execute(f"SELECT 1 FROM users WHERE user_id == {user_id}").fetchone()
    # if not user:
    user = cur.execute("INSERT INTO users VALUES(?, ?, ?, ?)",
                       (new_user.user_id, new_user.nick, new_user.user_name, new_user.is_administrator))
    db.commit()
    return user


async def create_resource(new_resource: Resource) -> sq.Cursor:
    resource = cur.execute("INSERT INTO resources VALUES (?, ?, ?, ?, ?)", (new_resource.resource_name,
                                                                            new_resource.domain_name,
                                                                            new_resource.ip_address,
                                                                            json.dumps(new_resource.users_id),
                                                                            new_resource.describe))
    db.commit()
    return resource


async def edit_resources(state, resource_name) -> None:
    async with state.proxy() as data:
        cur.execute(f"UPDATE resources SET resource_name = '{data['resource_name']}',"
                    f"ip_address = '{data['ip_address']}',"
                    f"domain_name = '{data['domain_name']}'"
                    f"WHERE resource_name == {resource_name}")
        db.commit()


async def get_admin() -> list:
    return cur.execute("SELECT user_id FROM users WHERE is_administrator == 1").fetchall()
