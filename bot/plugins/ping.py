from datetime import datetime

from hydrogram import Client, filters
from hydrogram.types import Message

from bot.utils import commands

@Client.on_message(filters.command("ping"))
async def ping(c: Client, m: Message):
    first = datetime.now()
    sent = await m.reply_text("<b>Pong!</b>")
    second = datetime.now()
    await sent.edit_text(f"<b>Pong!</b> <code>{(second - first).microseconds / 1000}</code>ms")


commands.add_command("ping", "info")
