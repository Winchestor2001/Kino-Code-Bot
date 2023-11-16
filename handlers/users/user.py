import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, WrongFileIdentifier
from telegraph import Telegraph

from data.config import CHANNELS_STATUS, ADMINS, POSTER_IMAGE, SEND_POSTER_IMAGE
from keyboards.inline.admin_btns import channels_btn, admin_panel_btn, add_channel_btn, cencel_send_btn, add_admin_btn, \
    remove, del_channel_btn
from keyboards.inline.user_btns import movie_channel_url_btn
from loader import dp, bot
from states.AllStates import MyStates
from database.connections import add_user, get_channels, get_admins, delete_movie_code, get_movies_list, \
    delete_all_movies, get_movie, add_new_channel, get_channel_by_id, delete_channel, add_new_admin, delete_admin, \
    add_new_movie, get_all_users, update_movie_views
from utils.misc.dot_env import edit_env_file


async def channels_check_func(user_id):
    channels, count_channels = await get_channels()
    if count_channels == 0:
        return "success"
    else:
        unsubs = []
        for row in channels:
            channel_name = row['channel_name']
            channel_id = row['channel_id']
            channel_link = row['channel_link']

            check_user = await bot.get_chat_member(channel_id, user_id)
            if check_user.status not in CHANNELS_STATUS:
                unsubs.append(
                    {
                        'channel_name': channel_name,
                        'channel_link': channel_link,
                    }
                )

    if len(unsubs) == 0:
        return "success"
    else:
        return await channels_btn(unsubs)


async def welcome(message: Message):
    user_id = message.from_user.id

    await add_user(user_id)
    text = await channels_check_func(user_id)
    if "success" in text:
        await message.answer(f"Kino <b>KODINI</b> yuboring✅...")
    else:
        btn = text
        await message.answer(f"<b>❌ TAYORMASSIZ ❌</b>\n\n"
                             f"👉 Sizga kerakli kinoni korish uchun kanalarga obuna bolishingiz kerak.\n\n"
                             f"Quyidagi kanalarga obuna boling👇 \n"
                             f"va tekshirish uchun <b>OBUNA BO'LDIM</b> tugmasini bosing!",
                             disable_web_page_preview=True,
                             reply_markup=btn)


async def admin_panel_handler(message: Message):
    user_id = message.from_user.id
    admins, users = await get_admins()
    if user_id in admins:
        btn = await admin_panel_btn()
        await message.answer("<code>/del 200</code> kino o`chirish\n"
                             "<code>/kodlar https://...</code> kinolar kanali\n"
                             "<code>/list</code> kinolar ro`yxati\n"
                             "<code>/delmovie</code> barcha kinolarni o`chirish")
        await message.answer(f"Siz admin paneldasiz:\n\n"
                             f"Bot a'zolari: <b>{users}</b> ta", reply_markup=btn)


async def delete_code_handler(message: Message):
    user_id = message.from_user.id
    code = message.get_args()

    admins, _ = await get_admins()

    if user_id in ADMINS or user_id in admins:
        if code.isdigit():
            if await delete_movie_code(code):
                await message.answer(f"✅ <b>{code} kodi uchirildi!</b>")
            else:
                await message.answer(f"⚠️ {code} kod mavjud emas!")
        else:
            await message.answer(f"Xato komanda")


async def add_default_channel_handler(message: Message):
    user_id = message.from_user.id
    channel_link = message.get_args()

    admins, _ = await get_admins()

    if user_id in ADMINS or user_id in admins:
        if channel_link.startswith("https://t.me"):
            await edit_env_file(channel_link)
            await message.answer(f"<b>✅ Kanal linki saqlandi!</b>")
        else:
            await message.answer(f"Xato komanda")


async def code_list_handler(message: Message):
    telegraph = Telegraph()
    telegraph.create_account(short_name='1337')
    user_id = message.from_user.id
    admins, users = await get_admins()

    if user_id in ADMINS or user_id in admins:
        movies, movies_count = await get_movies_list()
        if movies_count == 0:
            await bot.send_message(user_id, f"Bazada kinolar yoq!")
        else:
            total_text = []
            for m in movies:
                code = m['movie_code']
                title = m['movie_title']
                text = f"<b>{code}</b> - {title}"
                total_text.append(text)

            result = ('<br>'.join(total_text))
            response = telegraph.create_page(
                'Kinolar kodi:',
                html_content=f'{result}'
            )

            await message.answer(response['url'])


async def clear_movies_handler(message: Message):
    user_id = message.from_user.id
    admins, users = await get_admins()

    if user_id in ADMINS or user_id in admins:
        await delete_all_movies()
        await message.answer("Barcha kinolar o'chirildi!")


async def movie_code_handler(message: Message):
    user_id = message.from_user.id
    code = message.text

    if code.isdigit():
        movie_info = await get_movie(code)
        check_channel = await channels_check_func(user_id)
        if "success" in check_channel:
            if movie_info:
                for m in movie_info:
                    try:
                        btn = await movie_channel_url_btn()
                        views = await update_movie_views(m['movie_code'])
                        await bot.send_video(user_id, m['movie_id'], caption=f"🔢 <b>Film kodi:</b> #{m['movie_code']}\n"
                                                                             f"📄 <b>Film Nomi:</b> {m['movie_title']}\n\n"
                                                                             f"📥 Yuklangan: <b>{views}</b> marotaba",
                                             reply_markup=btn)
                    except WrongFileIdentifier:
                        await message.answer(f"⚠️ <b>{message.text}</b> kodi mavjud emas.")
            else:
                await message.answer(f"⚠️ <b>{message.text}</b> kodi mavjud emas.")

        else:
            btn = check_channel
            await message.answer(f"<b>❌ TAYORMASSIZ ❌</b>\n\n"
                                 f"👉 Sizga kerakli kinoni korish uchun kanalarga obuna bolishingiz kerak.\n\n"
                                 f"Quyidagi kanalarga obuna boling👇 \n"
                                 f"va tekshirish uchun <b>OBUNA BO'LDIM</b> tugmasini bosing!",
                                 disable_web_page_preview=True,
                                 reply_markup=btn)


async def check_channel_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.split("\n")
    prefix = '-100'
    try:
        if len(text) == 3:
            text = [item.strip() for item in text]
            channel_name, channel_id, channel_link = text

            if channel_id.isdigit() or channel_id.startswith('-100'):
                bot_id = await bot.get_me()
                status = await bot.get_chat_member(chat_id=prefix + channel_id, user_id=bot_id.id)

                if status.status != 'administrator':
                    await message.answer('Meni oldin kanalda admin qiling !')

                else:
                    await message.answer(f"✅ Nomi: {channel_name}\n"
                                         f"✅ Link: {channel_link}", disable_web_page_preview=True, reply_markup=remove)

                    channel_id = prefix + channel_id
                    await add_new_channel(channel_name, channel_id, channel_link)
                    channels, _ = await get_channels()

                    btn = await add_channel_btn(channels)

                    await message.answer(
                        text=f"📶 Kanallar ro'yxati:",
                        reply_markup=btn
                    )
                await state.finish()

        else:
            await message.answer(
                'Kanal qushish uchun shu kurinishda yozing:\n\n<em>KANAL NOMI\nKANAL ID\nhttps://t.me/+9DejWHHYHVVkMzg6</em>',
                disable_web_page_preview=True)

    except ChatNotFound:
        await bot.send_message(user_id, '<b>Kanal topilmadi!</b>')


async def check_admin_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.split("\n")

    if len(text) == 2:
        admin_name, admin_id = text

        if text[1].isdigit():
            await message.answer(f"✅ Admin Ismi: {admin_name}\n"
                                 f"✅ Admin IDsi: {admin_id}")

            await add_new_admin(admin_name, admin_id)

            admins = await get_admins(all_admins=False)

            btn = await add_admin_btn(admins)

            await message.answer(
                text=f"📶 Adminlar ro`yxati:",
                reply_markup=btn
            )
            await state.finish()

    else:
        await bot.send_message(user_id,
                               'Admin qushish uchun shu kurinishda yozing:\n\n<em>Admin Ismi\nAdmin IDsi</em>')


async def send_ads_handler(message: Message, state: FSMContext):
    text_type = message.content_type
    text = message.text
    rep_btn = message.reply_markup
    text_caption = message.html_text

    if text == '❌':
        await message.answer("❌", reply_markup=remove)
        await state.finish()
        return await admin_panel_handler(message)
    else:
        sends = 0
        sends_error = 0
        await message.answer("Xabarni yuborish boshlandi....", reply_markup=remove)
        await admin_panel_handler(message)
        await state.finish()

        users = await get_all_users()

        for u in users:
            try:
                if text_type == 'text':
                    await bot.send_message(u, text, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.05)

                elif text_type == "photo":
                    await bot.send_photo(u, message.photo[-1].file_id, caption=text_caption,
                                         reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.05)

                elif text_type == "video":
                    await bot.send_video(u, message.video.file_id, caption=text_caption, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.05)

                elif text_type == "animation":
                    await bot.send_animation(u, message.animation.file_id, caption=text_caption,
                                             reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.05)

                elif text_type == "document":
                    await bot.send_document(u, message.document.file_id, caption=text_caption, reply_markup=rep_btn)
                    sends += 1
                    await asyncio.sleep(0.05)

            except BotBlocked:
                sends_error += 1
                continue

        if sends == 0:
            await message.answer("⚠️ Xabar xechkimga etibormadi!")
        else:
            await message.answer(
                f"Siz yuborgan xabar <b>{sends}</b> ta a'zoga yetib bordi va <b>{sends_error}</b> ta a'zoga yetibormadi!"
            )


async def add_movie_state(message: Message, state: FSMContext):
    text = message.text
    content = message.content_type
    if text == '❌':
        await message.answer("❌", reply_markup=remove)
    else:
        caption = message.caption
        if content == 'video':
            movie_id = message.video.file_id
        else:
            movie_id = message.document.file_id

        cap_split = list([item for item in caption.split("\n", 1) if item != ''])
        movie_code, movie_title = cap_split
        await add_new_movie(movie_code, movie_title, movie_id)
        await message.answer(f"✅ Kino bazaga saqlandi!\n\n"
                             f"<code>{movie_code}</code> kodi orqali topishingiz mumkin!",
                             reply_markup=remove)

    await state.finish()
    return await admin_panel_handler(message)


async def back_callback(c: CallbackQuery):
    admins, users = await get_admins()

    btn = await admin_panel_btn()
    await c.message.edit_text(f"Siz admin paneldasiz:\n\n"
                              f"Bot a'zolari: <b>{users}</b> ta", reply_markup=btn)


async def del_panel_callback(c: CallbackQuery):
    user_id = c.from_user.id
    await bot.answer_callback_query(c.id)
    await bot.delete_message(user_id, c.message.message_id)
    await bot.send_message(user_id, "🏚 Bosh menu")


async def check_subscribe_callback(c: CallbackQuery):
    user_id = c.from_user.id

    text = await channels_check_func(user_id)
    if "success" in text:
        await c.message.edit_text(f"Kino <b>KODINI</b> yuboring✅...")
    else:
        await c.message.delete()
        btn = text
        await c.message.answer(f"<b>❌ TAYORMASSIZ ❌</b>\n\n"
                               f"👉 Sizga kerakli kinoni korish uchun kanalarga obuna bolishingiz kerak.\n\n"
                               f"Quyidagi kanalarga obuna boling👇 \n"
                               f"va tekshirish uchun <b>OBUNA BO'LDIM</b> tugmasini bosing!",
                               disable_web_page_preview=True,
                               reply_markup=btn)


async def add_channel_callback(c: CallbackQuery):
    user_id = c.from_user.id
    channels, count_channels = await get_channels()

    btn = await add_channel_btn(channels)

    await bot.answer_callback_query(c.id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=c.message.message_id,
        text=f"📶 Kanallar ro`yxati:",
        reply_markup=btn
    )


async def channel_config_callback(c: CallbackQuery):
    await c.answer()
    await c.message.delete()

    btn = await cencel_send_btn()
    await c.message.answer(
        text='Kanal qushish uchun shu kurinishda yozing:\n\n<em>KANAL NOMI\nKANAL ID\nhttps://t.me/+9DejWHHYHVVkMzg6</em>',
        reply_markup=btn,
        disable_web_page_preview=True
    )
    await MyStates.add_channel_check.set()


async def rek_callback(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer(f"VIDEO, AUDIO, RASIM, MATN lardan birini yuboring.\n\n"
                           f"Namuna 👇")

    btn = await cencel_send_btn()
    await c.message.answer_photo(
        photo=SEND_POSTER_IMAGE,
        caption=f"<em>Post xabarni yo`llang:</em>",
        reply_markup=btn)

    await MyStates.send_message.set()


async def add_movie_callback(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer(f"VIDEO yuboring.\n\n"
                           f"Namuna 👇")
    btn = await cencel_send_btn()
    await c.message.answer_photo(
        photo=POSTER_IMAGE,
        caption=f"<em>KINO KODI (150)\nKINO NOMI</em>",
        reply_markup=btn)
    await MyStates.add_movie.set()


async def add_admin_callback(c: CallbackQuery):
    await c.answer()
    admins = await get_admins(all_admins=False)

    btn = await add_admin_btn(admins)

    await c.message.edit_text(
        text=f"📶 Adminlar ro`yxati:",
        reply_markup=btn
    )


async def admin_config_callback(c: CallbackQuery):
    await c.answer()
    await c.message.delete()

    btn = await cencel_send_btn()
    await c.message.answer(
        text='Admin qushish uchun shu kurinishda yozing:\n\n<em>Admin Ismi\nAdmin IDsi</em>',
        reply_markup=btn
    )
    await MyStates.add_admin_check.set()


async def deladm_callback(c: CallbackQuery):
    cd = c.data
    await c.answer()

    del_adm = cd.split('_')[-1]
    await delete_admin(del_adm)

    admins = await get_admins(all_admins=False)
    btn = await add_admin_btn(admins)

    await c.message.edit_text(
        text=f"📶 Adminlar ro'yxati:",
        reply_markup=btn
    )


async def del_channel_callback(c: CallbackQuery):
    cd = c.data
    await c.answer()

    del_channel = cd.split('_')[1]
    await delete_channel(del_channel)

    channels, count_channels = await get_channels()

    btn = await add_channel_btn(channels)
    await c.message.edit_text(
        text=f"📶 Kanallar ro`yxati:",
        reply_markup=btn
    )


async def _100_id_callback(c: CallbackQuery):
    cd = c.data
    await c.answer()

    channel = await get_channel_by_id(cd)

    btn = await del_channel_btn(channel)
    await c.message.edit_text(
        text=f"📶 Kanallar ro'yxati:",
        reply_markup=btn
    )


def register_user_py(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start'], state='*')
    dp.register_message_handler(admin_panel_handler, commands=['admin'])
    dp.register_message_handler(delete_code_handler, commands=['del'])
    dp.register_message_handler(add_default_channel_handler, commands=['kodlar'])
    dp.register_message_handler(code_list_handler, commands=['list'])
    dp.register_message_handler(clear_movies_handler, commands=['delmovie'])
    dp.register_message_handler(movie_code_handler, content_types=['text'])
    dp.register_message_handler(check_channel_handler, content_types=['text'], state=MyStates.add_channel_check)
    dp.register_message_handler(check_admin_handler, content_types=['text'], state=MyStates.add_admin_check)
    dp.register_message_handler(send_ads_handler, content_types=['text', 'photo', 'video', 'animation', 'document'],
                                state=MyStates.send_message)
    dp.register_message_handler(add_movie_state, content_types=['video', 'text', 'document'], state=MyStates.add_movie)

    # callback
    dp.register_callback_query_handler(back_callback, text='back')
    dp.register_callback_query_handler(del_panel_callback, text='del_panel')
    dp.register_callback_query_handler(check_subscribe_callback, text='check_subscribe')
    dp.register_callback_query_handler(add_channel_callback, text='add_channel')
    dp.register_callback_query_handler(channel_config_callback, text='channel_config')
    dp.register_callback_query_handler(del_channel_callback, text_contains='delchannel_')
    dp.register_callback_query_handler(rek_callback, text='rek')
    dp.register_callback_query_handler(add_movie_callback, text='add_movie')
    dp.register_callback_query_handler(add_admin_callback, text='add_admin')
    dp.register_callback_query_handler(admin_config_callback, text='admin_config')
    dp.register_callback_query_handler(deladm_callback, text_contains='deladm_')
    dp.register_callback_query_handler(_100_id_callback, text_contains='-100')
