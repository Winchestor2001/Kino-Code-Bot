from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def movie_channel_url_btn(link):
    btn = InlineKeyboardMarkup()
    btn.add(
        InlineKeyboardButton("Boshqa kinolar kodlari 👉", url=link)
    )
    return btn

