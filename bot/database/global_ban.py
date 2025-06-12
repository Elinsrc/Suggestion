import os
import random

from .core import database

conn = database.get_conn()

async def user_add_to_ban(user_id: int):
    await conn.execute('INSERT INTO banned_users (user_id) VALUES (?)', (user_id,))
    await conn.commit()

async def user_remove_from_ban(user_id: int):
    await conn.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
    await conn.commit()

async def is_user_banned(user_id: int) -> bool:
    async with conn.execute('SELECT user_id FROM banned_users WHERE user_id = ?', (user_id,)) as cursor:
        return await cursor.fetchone() is not None
