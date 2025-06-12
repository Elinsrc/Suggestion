import os
from hydrogram import Client, filters
from hydrogram.types import Message

from config import FORWARDING_CHAT

from bot.utils.localization import Strings, use_chat_lang
from bot.database.global_ban import check_ban
from bot.utils import commands

@Client.on_message(filters.command(["suggestpost","sp"]))
@use_chat_lang
@check_ban
async def sendmedia(c: Client, m: Message, s: Strings):
    user = m.from_user
    user_name = user.username or user.first_name
    user_id = user.id

    text = ""
    if m.text:
        parts = m.text.split(maxsplit=1)
        if len(parts) > 1:
            text = parts[1]
    elif m.caption:
        parts = m.caption.split(maxsplit=1)
        if len(parts) > 1:
            text = parts[1]

    has_media = any(
        getattr(m, attr, None) is not None for attr in [
            'audio', 'photo', 'animation', 'document', 'video', 'voice'
        ]
    )

    if not has_media and not text:
        await m.reply_text(s("suggestpost_example"))
        return

    caption_text = f"👤 {user_name} (ID: {user_id})"
    if text:
        caption_text += f"\n💬 {text}"

    media_types = {
        'audio': c.send_audio,
        'photo': c.send_photo,
        'animation': c.send_animation,
        'document': c.send_document,
        'video': c.send_video,
        'voice': c.send_voice
    }

    for attr, send_func in media_types.items():
        media = getattr(m, attr, None)
        if media:
            file = await c.download_media(media)
            await send_func(
                chat_id=FORWARDING_CHAT,
                **{attr: file},
                caption=caption_text
            )
            os.remove(file)
            break
    else:
        await c.send_message(
            chat_id=FORWARDING_CHAT,
            text=caption_text
        )

commands.add_command("suggestpost", "general")
