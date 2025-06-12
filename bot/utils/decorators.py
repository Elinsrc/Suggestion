from __future__ import annotations

import asyncio
from functools import partial, wraps
from typing import TYPE_CHECKING

import hydrogram
from hydrogram import Client, StopPropagation
from hydrogram.enums import ChatType
from hydrogram.types import CallbackQuery, ChatPrivileges, Message
from hydrogram.methods import Decorators
from hydrogram.filters import Filter

from bot.utils.localization import (
    get_lang,
    get_locale_string,
)
from bot.utils.utils import check_perms


from bot.database.global_ban import is_user_banned

if TYPE_CHECKING:
    from collections.abc import Callable


def aiowrap(func: Callable) -> Callable:
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


def require_admin(
    permissions: ChatPrivileges | None = None,
    allow_in_private: bool = False,
    complain_missing_perms: bool = True,
):
    """Decorator that checks if the user is an admin in the chat.

    Parameters
    ----------
    permissions: ChatPrivileges
        The permissions to check for.
    allow_in_private: bool
        Whether to allow the command in private chats or not.
    complain_missing_perms: bool
        Whether to complain about missing permissions or not, otherwise the
        function will not be called and the user will not be notified.

    Returns
    -------
    Callable
        The decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: CallbackQuery | Message, *args, **kwargs):
            lang = await get_lang(message)
            s = partial(
                get_locale_string,
                lang,
            )

            if isinstance(message, CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
            elif isinstance(message, Message):
                sender = message.reply_text
                msg = message
            else:
                raise NotImplementedError(
                    f"require_admin can't process updates with the type '{message.__name__}' yet."
                )

            # We don't actually check private and channel chats.
            if msg.chat.type == ChatType.PRIVATE:
                if allow_in_private:
                    return await func(client, message, *args, *kwargs)
                return await sender(s("cmd_private_not_allowed"))
            if msg.chat.type == ChatType.CHANNEL:
                return await func(client, message, *args, *kwargs)
            has_perms = await check_perms(message, permissions, complain_missing_perms, s)
            if has_perms:
                return await func(client, message, *args, *kwargs)
            return None

        return wrapper

    return decorator


def stop_here(func: Callable) -> Callable:
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        finally:
            raise StopPropagation

    return wrapper


def command(
    self: hydrogram.Client | Filter | None = None,
    filters: Filter | None = None,
    group: int = 0,
    check_ban: bool | None = None,
):
    def decorator(func):
        async def wrapped(client, message, *args, **kwargs):
            if check_ban:
                lang = await get_lang(message)
                s = partial(
                    get_locale_string,
                    lang,
                )

                if message.from_user:
                    if await is_user_banned(message.from_user.id):
                        return await message.reply_text(s("banned_msg"))

            return await func(client, message, *args, **kwargs)

        if isinstance(self, hydrogram.Client):
            self.add_handler(hydrogram.handlers.MessageHandler(wrapped, filters), group)
        elif isinstance(self, Filter) or self is None:
            if not hasattr(func, "handlers"):
                func.handlers = []

            func.handlers.append((
                hydrogram.handlers.MessageHandler(wrapped, self),
                group if filters is None else filters,
            ))

        return func

    return decorator

Decorators.on_cmd = command
