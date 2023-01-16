from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton


admin_panel = InlineKeyboardMarkup()
admin_panel.row(InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                InlineKeyboardButton("Xabar junatish 📮", callback_data="rek"))
admin_panel.row(InlineKeyboardButton("➕ Admin qo'shish", callback_data="add_admin"),
                InlineKeyboardButton(text='Kino qushish 📽', callback_data='add_movie'))
admin_panel.row(InlineKeyboardButton("Ortga ↩️", callback_data="del_panel"))

channels_btn = InlineKeyboardMarkup()
chb11 = InlineKeyboardButton("✅ OBUNA BOLDIM ✅", callback_data="check_subscribe")
channels_btn.add(chb11)


add_channel_btn = InlineKeyboardMarkup(row_width=1)
del_channel_btn = InlineKeyboardMarkup(row_width=1)

add_admin_btn = InlineKeyboardMarkup(row_width=1)
del_admin_btn = InlineKeyboardMarkup(row_width=1)


remove = ReplyKeyboardRemove()

cencel_send_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cencel_send_btn.row("❌")


send_post_btn = InlineKeyboardMarkup(row_width=1)