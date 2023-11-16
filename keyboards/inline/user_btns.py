from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import MOVIES_CHANNEL_LINK


async def movie_channel_url_btn():
    btn = InlineKeyboardMarkup()
    btn.add(
        InlineKeyboardButton("Boshqa kinolar kodlari 👉", url=MOVIES_CHANNEL_LINK)
    )
    return btn

