from hydrogram.enums import ChatType

from bot.database import database
from bot.utils.consts import GROUP_TYPES

conn = database.get_conn()


async def add_chat(chat_id, chat_type):
    if chat_type == ChatType.PRIVATE:
        await conn.execute("INSERT INTO users (user_id) values (?)", (chat_id,))
        await conn.commit()
    elif chat_type in GROUP_TYPES:  # groups and supergroups share the same table
        await conn.execute("INSERT INTO groups (chat_id) values (?)", (chat_id,))
        await conn.commit()
    elif chat_type == ChatType.CHANNEL:
        await conn.execute("INSERT INTO channels (chat_id) values (?)", (chat_id,))
        await conn.commit()
    else:
        raise TypeError(f"Unknown chat type '{chat_type}'.")
    return True


async def chat_exists(chat_id, chat_type):
    if chat_type == ChatType.PRIVATE:
        cursor = await conn.execute("SELECT user_id FROM users where user_id = ?", (chat_id,))
        row = await cursor.fetchone()
        return bool(row)
    if chat_type in GROUP_TYPES:  # groups and supergroups share the same table
        cursor = await conn.execute("SELECT chat_id FROM groups where chat_id = ?", (chat_id,))
        row = await cursor.fetchone()
        return bool(row)
    if chat_type == ChatType.CHANNEL:
        cursor = await conn.execute("SELECT chat_id FROM channels where chat_id = ?", (chat_id,))
        row = await cursor.fetchone()
        return bool(row)
    raise TypeError(f"Unknown chat type '{chat_type}'.")
