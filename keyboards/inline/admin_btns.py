from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton


remove = ReplyKeyboardRemove()


async def admin_panel_btn():
    btn = InlineKeyboardMarkup()
    btn.row(InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                    InlineKeyboardButton("Xabar junatish 📮", callback_data="rek"))
    btn.row(InlineKeyboardButton("➕ Admin qo'shish", callback_data="add_admin"),
                    InlineKeyboardButton(text='Kino qushish 📽', callback_data='add_movie'))
    btn.row(InlineKeyboardButton("Ortga ↩️", callback_data="del_panel"))

    return btn


async def channels_btn(channels):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.add(
        *[InlineKeyboardButton(f"{item['channel_name']}", url=f"{item['channel_link']}") for item in channels],
        InlineKeyboardButton("✅ OBUNA BOLDIM ✅", callback_data="check_subscribe")
    )
    return btn


async def add_channel_btn(channels):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.add(
        InlineKeyboardButton("➕", callback_data="channel_config"),
        InlineKeyboardButton("➕ Zayavkalik", callback_data="channel_config_invite"),
        InlineKeyboardButton("Ortga ↩️", callback_data="back"),
        *[InlineKeyboardButton(f"{item['channel_name']}", callback_data=f"{item['channel_id']}") for item in channels]
    )
    return btn


async def del_channel_btn(channel):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.add(
        InlineKeyboardButton("Ortga ↩️", callback_data="back"),
        InlineKeyboardButton("❌", callback_data=f"delchannel_{channel['channel_id']}"),
        InlineKeyboardButton(f"{channel['channel_name']}", url=f"{channel['channel_link']}"),
    )
    return btn


async def add_admin_btn(admins):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.add(
        InlineKeyboardButton("➕", callback_data="admin_config"),
        InlineKeyboardButton("Ortga ↩️", callback_data="back"),
        *[InlineKeyboardButton(f"{item['admin_name']}", callback_data=f"deladm_{item['admin_id']}") for item in admins]
    )
    return btn


async def del_admin_btn():
    btn = InlineKeyboardMarkup(row_width=1)
    btn.add(

    )
    return btn


async def cencel_send_btn():
    btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn.row("❌")
    return btn

