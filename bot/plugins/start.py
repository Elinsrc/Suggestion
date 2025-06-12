from hydrogram import Client, filters
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.utils import commands
from bot.utils.localization import Strings, use_chat_lang

from hydrogram.enums import ParseMode

# Using a low priority group so deeplinks will run before this and stop the propagation.
@Client.on_message(filters.command("start") & filters.private, group=2)
@Client.on_callback_query(filters.regex("^start_back$"))
@use_chat_lang
async def start_pvt(c: Client, m: Message | CallbackQuery, s: Strings):
    if isinstance(m, CallbackQuery):
        msg = m.message
        send = msg.edit_text
    else:
        msg = m
        send = msg.reply_text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(s("start_commands_btn"), callback_data="commands"),
            ],
            [
                InlineKeyboardButton(s("start_language_btn"), callback_data="chlang"),
            ],
        ]
    )
    await send(s("start_msg"), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


@Client.on_message(filters.command("start") & filters.group, group=2)
@use_chat_lang
async def start_grp(c: Client, m: Message | CallbackQuery, s: Strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    s("start_chat"),
                    url=f"https://t.me/{c.me.username}?start=start",
                )
            ]
        ]
    )
    await m.reply_text(s("start_msg"), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
