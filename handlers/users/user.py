import asyncio
import sys
import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from telegraph import Telegraph

from data.config import CHANNELS_STATUS, ADMINS
from keyboards.inline.admin_btns import channels_btn, admin_panel, add_channel_btn, cencel_send_btn, add_admin_btn, \
    remove, send_post_btn, del_admin_btn, del_channel_btn
from loader import dp, bot
from database.models import *
from states.AllStates import MyStates


async def showChannels():
    with db:
        channels = Channels.select()
    channels_btn.inline_keyboard.clear()
    for row in channels:
        text = row.channel_name
        id = row.channel_id
        link = row.channel_link

        chb = InlineKeyboardButton(text=text, url=link)
        channels_btn.add(chb)
    channels_btn.add(InlineKeyboardButton("✅ OBUNA BO'LDIM ✅", callback_data="check_subscribe"))


async def channelsCheckFunc(user_id):
    try:
        with db:
            channels = Channels.select()
            count_channels = Channels.select().count()
            if count_channels == 0:
                return "True"
            else:
                channels_btn.inline_keyboard.clear()
                nums = 0
                for row in channels:
                    text = row.channel_name
                    id = row.channel_id
                    link = row.channel_link

                    channel_id = id

                    check_user = await bot.get_chat_member(channel_id, user_id, )
                    if check_user.status in CHANNELS_STATUS:
                        nums += 0
                    else:
                        nums += 1
                        chb = InlineKeyboardButton(text=text, url=link)
                        channels_btn.add(chb)

            if nums == 0:
                return f"True"
            else:
                return f"False"


    except Exception as ex:
        # pass
        print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno}')


async def welcome(message: Message):
    user_id = message.from_user.id

    try:
        with db:
            Users.get_or_create(user_id=user_id)
        text = await channelsCheckFunc(user_id)
        if text == "True":
            await bot.send_message(user_id, f"Kino <b>KODINI</b> yuboring✅...")
        elif text == "False":
            await showChannels()
            await bot.send_message(user_id, f"<b>❌ TAYORMASSIZ ❌</b>\n\n"
                                            f"👉 Sizga kerakli kinoni korish uchun kanalarga obuna bolishingiz kerak.\n\n"
                                            f"Quyidagi kanalarga obuna boling👇 \n"
                                            f"va tekshirish uchun <b>OBUNA BO'LDIM</b> tugmasini bosing!",
                                   disable_web_page_preview=True,
                                   reply_markup=channels_btn)
    except Exception as ex:
        print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno}')


async def adminPanelFunc(message: Message):
    user_id = message.from_user.id
    admins = []
    with db:
        db_admins = Admins.select()
        users = Users.select().count()
        for da in db_admins:
            admins.append(da.admin_id)

    if user_id in ADMINS or user_id in admins:
        await bot.send_message(user_id, f"Siz admin paneldasiz:\n\n"
                                        f"Bot a'zolari: <b>{users}</b> ta", reply_markup=admin_panel)


async def deleteCodeFunc(message: Message):
    user_id = message.from_user.id
    text = message.text.split(' ')

    admins = []
    with db:
        db_admins = Admins.select()
        for da in db_admins:
            admins.append(da.admin_id)

    if user_id in ADMINS or user_id in admins:
        await bot.send_message(user_id, f"✅ <b>{text[1]} kodi uchirildi!</b>")
        with db:
            Movies.delete().where(Movies.movie_code == text[1]).execute()


async def codeListFunc(message: Message):
    telegraph = Telegraph()
    telegraph.create_account(short_name='1337')
    user_id = message.from_user.id
    admins = []
    with db:
        db_admins = Admins.select()
        for da in db_admins:
            admins.append(da.admin_id)

    if user_id in ADMINS or user_id in admins:
        with db:
            all_movies = Movies.select().order_by(Movies.movie_code.asc())
            movies_count = Movies.select().count()
        if movies_count == 0:
            await bot.send_message(user_id, f"Bazada kinolar yoq!")
        else:
            totel_text = []
            for m in all_movies:
                code = m.movie_code
                title = m.movie_title
                text = f"<b>{code}</b> - {title}"
                totel_text.append(text)

            result = ('<br>'.join(totel_text))
            response = telegraph.create_page(
                'Kinolar kodi:',
                html_content=f'{result}'
            )

            await bot.send_message(user_id, response['url'])


async def clearMoviestFunc(message: Message):
    user_id = message.from_user.id
    admins = []
    with db:
        db_admins = Admins.select()
        for da in db_admins:
            admins.append(da.admin_id)

    if user_id in ADMINS or user_id in admins:
        with db:
            Movies.delete().execute()

        await message.answer("Barcha kinolar o'chirildi!")


async def movieCodeHandler(message: Message):
    user_id = message.from_user.id
    text = message.text
    if text.isdigit():
        with db:
            movie_info = Movies.select().where(Movies.movie_code == text)
            bot_name_link = await bot.get_me()
            try:
                check_channel = await channelsCheckFunc(user_id)
                if check_channel == "True":
                    if movie_info.exists():
                        for m in movie_info:
                            await bot.send_video(user_id, m.movie_id, caption=f"🔢 <b>Film kodi:</b> #{m.movie_code}\n"
                                                                              f"📄 <b>Film Nomi:</b> {m.movie_title}\n\n"
                                                                              f"By @{bot_name_link.username}")

                    else:
                        await bot.send_message(user_id, f"⚠️ <b>{message.text}</b> kodi mavjud emas.")



                elif check_channel == "False":
                    await showChannels()
                    await bot.send_message(user_id, f"<b>❌ TAYORMASSIZ ❌</b>\n\n"
                                                    f"👉 Sizga kerakli kinoni korish uchun kanalarga obuna bolishingiz kerak.\n\n"
                                                    f"Quyidagi kanalarga obuna boling👇 \n"
                                                    f"va tekshirish uchun <b>OBUNA BO'LDIM</b> tugmasini bosing!",
                                           disable_web_page_preview=True,
                                           reply_markup=channels_btn)

            except Exception as ex:
                print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno}')
    else:
        await bot.send_message(user_id, f"⚠️ <b>{message.text}</b> kodi mavjud emas.")


async def checkChannelFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.split(" + ")
    prefix = '-100'
    try:
        if len(text) == 3:
            name = text[0]
            id = text[1]
            link = text[2]

            if id.isdigit():
                bot_id = await bot.get_me()
                status = await bot.get_chat_member(chat_id=prefix + id, user_id=bot_id.id)

                if status.status != 'administrator':
                    await bot.send_message(message.chat.id, 'Meni oldin kanalda admin qiling !')

                else:
                    await bot.send_message(user_id, f"✅ Nomi: {name}\n"
                                                    f"✅ Link: {link}", disable_web_page_preview=True)

                    channel_id = prefix + id
                    with db:
                        Channels.get_or_create(channel_name=name, channel_id=channel_id, channel_link=link)
                        channels = Channels.select()

                    add_channel_btn.inline_keyboard.clear()
                    achb_1 = InlineKeyboardButton("➕", callback_data="channel_config")
                    achb_2 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
                    add_channel_btn.add(achb_1, achb_2)
                    for row in channels:
                        text = row.channel_name
                        id = row.channel_id
                        link = row.channel_link

                        add_btn = InlineKeyboardButton(text, callback_data=id)
                        add_channel_btn.add(add_btn)

                    await bot.send_message(
                        chat_id=user_id,
                        text=f"📶 Kanallar ro'yxati:",
                        reply_markup=add_channel_btn
                    )
                await state.finish()

        else:
            await bot.send_message(user_id,
                                   'Kanal qushish uchun shu kurinishda yozing:\n\n<em>KANAL NOMI + KANAL ID + https://t.me/+9DejWHHYHVVkMzg6</em>',
                                   disable_web_page_preview=True, reply_markup=cencel_send_btn)

    except Exception as ex:
        print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno}')
        await bot.send_message(user_id, '<b>Kanal topilmadi!</b>')


async def checkAdminFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.split(" + ")
    add_admin_btn.inline_keyboard.clear()

    if len(text) == 2:
        name = text[0]
        id = text[1]

        if text[1].isdigit():
            await bot.send_message(user_id, f"✅ Admin Ismi: {name}\n"
                                            f"✅ Admin IDsi: {id}")

            with db:
                Admins.get_or_create(admin_id=id, admin_name=name)
                db_admins = Admins.select()

            achb_1 = InlineKeyboardButton("➕", callback_data="admin_config")
            achb_2 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
            add_admin_btn.add(achb_1, achb_2)

            for row in db_admins:
                text = row.admin_name
                id = row.admin_id

                add_btn = InlineKeyboardButton(text, callback_data=f"new_{id}")
                add_admin_btn.add(add_btn)

            await bot.send_message(
                chat_id=user_id,
                text=f"📶 Adminlar ro'yxati:",
                reply_markup=add_admin_btn
            )
            add_admin_btn.inline_keyboard.clear()
            await state.finish()

    else:
        await bot.send_message(user_id,
                               'Admin qushish uchun shu kurinishda yozing:\n\n<em>Admin Ismi + Admin IDsi</em>')


async def sendAdsFunc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text_type = message.content_type
    text = message.text
    text_caption = message.html_text
    rep_btn = message.reply_markup
    if text == '❌':
        await bot.send_message(user_id, "❌", reply_markup=remove)
        await bot.send_message(user_id, f"Siz admin paneldasiz:", reply_markup=admin_panel)
        await state.finish()
    else:
        admins = []
        users = []
        with db:
            for da in Admins.select():
                admins.append(da.admin_id)
            for user in Users.select():
                users.append(user)

        if user_id in ADMINS or user_id in admins:
            sends = 0
            sends_error = 0
            send_post_btn.inline_keyboard.clear()
            await bot.send_message(user_id, "Xabarni yuborishni boshladim....", reply_markup=remove)
            await bot.send_message(user_id, f"Siz admin paneldasiz:", reply_markup=admin_panel)
            await state.finish()

            for u in users:
                try:
                    if text_type == 'text':
                        await bot.send_message(u, text, reply_markup=rep_btn)
                        sends += 1
                        await asyncio.sleep(0.03)

                    elif text_type == "photo":
                        await bot.send_photo(u, message.photo[-1].file_id, caption=text_caption,
                                             reply_markup=rep_btn)
                        sends += 1
                        await asyncio.sleep(0.03)

                    elif text_type == "video":
                        await bot.send_video(u, message.video.file_id, caption=text_caption, reply_markup=rep_btn)
                        sends += 1
                        await asyncio.sleep(0.03)

                    elif text_type == "animation":
                        await bot.send_animation(u, message.animation.file_id, caption=text_caption,
                                                 reply_markup=rep_btn)
                        sends += 1
                        await asyncio.sleep(0.03)

                    elif text_type == "document":
                        await bot.send_document(u, message.document.file_id, caption=text_caption, reply_markup=rep_btn)
                        sends += 1
                        await asyncio.sleep(0.03)


                except BotBlocked as e:
                    sends_error += 1
                    continue

                except TelegramAPIError as e:
                    await asyncio.sleep(0.3)
                    continue

                except Exception as ex:
                    # print(f'{type(ex).__name__}: {ex} | Line: {sys.exc_info()[-1].tb_lineno} ****** {ex}')
                    sends_error += 1
                    continue

            if sends == 0:
                await bot.send_message(user_id, "⚠️ Xabar xechkimga etibormadi!")
            else:
                await bot.send_message(user_id,
                                       f"Siz yuborgan xabar <b>{sends}</b> ta a'zoga yetib bordi va <b>{sends_error}</b> ta a'zoga yetibormadi!")


async def addMovie(message: Message, state: FSMContext):
    user_id = message.from_user.id

    admins = []
    with db:
        db_admins = Admins.select()
        for da in db_admins:
            admins.append(da.admin_id)

    if user_id in ADMINS or user_id in admins:
        try:
            if message.text == '❌':
                await bot.send_message(user_id, "❌", reply_markup=remove)
                await bot.send_message(user_id, f"Siz admin paneldasiz:", reply_markup=admin_panel)
                await state.finish()
            else:
                caption = message.caption
                movie_id = message.video.file_id
                spliting = caption.split("\n", 1)
                with db:
                    Movies.get_or_create(movie_code=spliting[0], movie_title=spliting[1], movie_id=movie_id)
                    users = Users.select().count()
                await bot.send_message(user_id, f"✅ Kino bazaga saqlandi!\n\n"
                                                f"<code>{spliting[0]}</code> kodi orqali topishingiz mumkin!",
                                       reply_markup=remove)

                await bot.send_message(user_id, f"Siz admin paneldasiz:\n\n"
                                                f"Bot a'zolari: <b>{users}</b> ta", reply_markup=admin_panel)

                await state.finish()
        except:
            await bot.send_message(user_id, "Xatolik yuz berdi!")


async def back_callback(c: CallbackQuery):
    user_id = c.from_user.id
    await bot.answer_callback_query(c.id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=c.message.message_id,
        text=f"Siz admin paneldasiz:",
        reply_markup=admin_panel
    )


async def del_panel_callback(c: CallbackQuery):
    user_id = c.from_user.id
    await bot.answer_callback_query(c.id)
    await bot.delete_message(user_id, c.message.message_id)
    await bot.send_message(user_id, "🏚 Bosh menu")


async def check_subscribe_callback(c: CallbackQuery):
    user_id = c.from_user.id
    text = await channelsCheckFunc(user_id)
    if text == "True":
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=c.message.message_id,
            text=f"Hammasini bajardingiz kino <b>KODINI</b> yuboring✅")

    elif text == "False":
        await showChannels()
        await bot.answer_callback_query(c.id, text=f"❗️TO'LIQ BAJARING❗️ \n\n"
                                                   f"👉 Sizga kerakli kinoni korish uchun kanalarga obuna bolishingiz kerak.\n\n"
                                                   f"Quyidagi kanalarga obuna boling👇 \n"
                                                   f'va tekshirish uchun " OBUNA BO`LDIM " tugmasini qayta bosing!',
                                        show_alert=True)


async def add_channel_callback(c: CallbackQuery):
    user_id = c.from_user.id
    with db:
        channels = Channels.select()
    add_channel_btn.inline_keyboard.clear()

    achb_1 = InlineKeyboardButton("➕", callback_data="channel_config")
    achb_2 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
    add_channel_btn.add(achb_1, achb_2)

    for row in channels:
        text = row.channel_name
        id = row.channel_id
        link = row.channel_link

        add_btn = InlineKeyboardButton(text, callback_data=id)
        add_channel_btn.add(add_btn)

    await bot.answer_callback_query(c.id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=c.message.message_id,
        text=f"📶 Kanallar ro`yxati:",
        reply_markup=add_channel_btn
    )
    add_channel_btn.inline_keyboard.clear()


async def channel_config_callback(c: CallbackQuery):
    add_channel_btn.inline_keyboard.clear()
    add_channel_btn.add(InlineKeyboardButton("Ortga ↩️", callback_data="back"))

    await MyStates.add_channel_check.set()

    await bot.answer_callback_query(c.id)
    await bot.edit_message_text(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        text='Kanal qushish uchun shu kurinishda yozing:\n\n<em>KANAL NOMI + KANAL ID + https://t.me/+9DejWHHYHVVkMzg6</em>',
        reply_markup=add_channel_btn,
        disable_web_page_preview=True
    )


async def rek_callback(c: CallbackQuery):
    user_id = c.from_user.id
    await MyStates.send_message.set()
    await bot.delete_message(chat_id=c.message.chat.id, message_id=c.message.message_id)
    await bot.send_message(user_id, f"VIDEO, AUDIO, RASIM, MATN lardan birini yuboring.\n\n"
                                    f"Namuna 👇")
    await bot.send_photo(
        chat_id=user_id,
        photo="https://i.ytimg.com/vi/JFcFsIrI2fU/maxresdefault.jpg",
        caption=f"<em>MATIN (text)</em>\n\n<em>knopka nomi + t.me/xavola</em>",
        reply_markup=cencel_send_btn)


async def add_movie_callback(c: CallbackQuery):
    user_id = c.from_user.id
    await MyStates.add_movie.set()
    await bot.delete_message(chat_id=c.message.chat.id, message_id=c.message.message_id)
    await bot.send_message(user_id, f"VIDEO yuboring.\n\n"
                                    f"Namuna 👇")
    await bot.send_photo(
        chat_id=user_id,
        photo="https://resizing.flixster.com/OQaP05A_ZDeHblCh7Tvim0eo8ts=/300x300/v2/https://resizing.flixster.com/6XUccibsh32LRSR3OYJu-eAz7uA=/ems.ZW1zLXByZC1hc3NldHMvbW92aWVzLzdjMThmNWI3LTBiMTQtNDFhOS05OTEyLTJhNTdlZGMzZWJiNi5qcGc=",
        caption=f"<em>KINO KODI (150) + KINO NOMI</em>",
        reply_markup=cencel_send_btn)


async def add_admin_callback(c: CallbackQuery):
    user_id = c.from_user.id
    with db:
        db_admins = Admins.select()

    add_admin_btn.inline_keyboard.clear()

    achb_1 = InlineKeyboardButton("➕", callback_data="admin_config")
    achb_2 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
    add_admin_btn.add(achb_1, achb_2)

    for row in db_admins:
        text = row.admin_name
        id = row.admin_id

        add_btn = InlineKeyboardButton(text, callback_data=f"new_{id}")
        add_admin_btn.add(add_btn)

    await bot.answer_callback_query(c.id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=c.message.message_id,
        text=f"📶 Adminlar ro`yxati:",
        reply_markup=add_admin_btn
    )
    add_admin_btn.inline_keyboard.clear()


async def admin_config_callback(c: CallbackQuery):
    add_admin_btn.inline_keyboard.clear()
    add_admin_btn.add(InlineKeyboardButton("Ortga ↩️", callback_data="back"))

    await MyStates.add_admin_check.set()

    await bot.answer_callback_query(c.id)
    await bot.edit_message_text(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        text='Admin qushish uchun shu kurinishda yozing:\n\n<em>Admin Ismi + Admin IDsi</em>',
        reply_markup=add_admin_btn
    )


async def deladm_callback(c: CallbackQuery):
    user_id = c.from_user.id
    cd = c.data

    del_adm = cd.split('_')[1]
    with db:
        Admins.delete().where(Admins.admin_id == del_adm).execute()
        db_admins = Admins.select()

    add_admin_btn.inline_keyboard.clear()
    achb_1 = InlineKeyboardButton("➕", callback_data="admin_config")
    achb_2 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
    add_admin_btn.add(achb_1, achb_2)
    for row in db_admins:
        text = row.admin_name
        id = row.admin_id

        add_btn = InlineKeyboardButton(text, callback_data=f"new_{id}")
        add_admin_btn.add(add_btn)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=c.message.message_id,
        text=f"📶 Adminlar ro'yxati:",
        reply_markup=add_admin_btn
    )


async def new_channel_callback(c: CallbackQuery):
    cd = c.data
    spliting = cd.split('_')
    del_link = f'deladm_{spliting[1]}'
    del_admin_btn.inline_keyboard.clear()
    await bot.answer_callback_query(c.id)

    dchb_1 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
    dchb_2 = InlineKeyboardButton("❌", callback_data=f"{del_link}")
    del_admin_btn.add(dchb_1, dchb_2)

    with db:
        channel = Admins.select().where(Admins.admin_id == int(spliting[1]))
    for row in channel:
        text = row.admin_name
        id = row.admin_id
        del_admin_btn.add(InlineKeyboardButton(text, callback_data="id"))

    await bot.edit_message_text(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        text=f"📶 Adminlar ro'yxati:",
        reply_markup=del_admin_btn
    )


async def del_channel_callback(c: CallbackQuery):
    user_id = c.from_user.id
    cd = c.data

    del_channel = cd.split('_')[1]
    with db:
        Channels.delete().where(Channels.channel_id == del_channel).execute()
        channels = Channels.select()

    add_channel_btn.inline_keyboard.clear()
    achb_1 = InlineKeyboardButton("➕", callback_data="channel_config")
    achb_2 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
    add_channel_btn.add(achb_1, achb_2)
    for row in channels:
        text = row.channel_name
        id = row.channel_id
        link = row.channel_link

        add_btn = InlineKeyboardButton(text, callback_data=id)
        add_channel_btn.add(add_btn)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=c.message.message_id,
        text=f"📶 Kanallar ro'yxati:",
        reply_markup=add_channel_btn
    )


async def _100_id_callback(c: CallbackQuery):
    cd = c.data
    msg = c.message.chat.id

    del_link = f'delchannel_{cd}'
    del_channel_btn.inline_keyboard.clear()
    await bot.answer_callback_query(c.id)

    dchb_1 = InlineKeyboardButton("Ortga ↩️", callback_data="back")
    dchb_2 = InlineKeyboardButton("❌", callback_data=f"{del_link}")
    del_channel_btn.add(dchb_1, dchb_2)

    with db:
        channel = Channels.select().where(Channels.channel_id == cd)
    for row in channel:
        text = row.channel_name
        id = row.channel_id
        link = row.channel_link
        del_channel_btn.add(InlineKeyboardButton(text, url=link))

    await bot.edit_message_text(
        chat_id=msg,
        message_id=c.message.message_id,
        text=f"📶 Kanallar ro'yxati:",
        reply_markup=del_channel_btn
    )


# user_id = c.from_user.id
def register_user_py(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start'])
    dp.register_message_handler(adminPanelFunc, commands=['admin'])
    dp.register_message_handler(deleteCodeFunc, commands=['del'])
    dp.register_message_handler(codeListFunc, commands=['list'])
    dp.register_message_handler(clearMoviestFunc, commands=['delmovie'])
    dp.register_message_handler(movieCodeHandler, content_types=['text'])
    dp.register_message_handler(checkChannelFunc, content_types=['text'], state=MyStates.add_channel_check)
    dp.register_message_handler(checkAdminFunc, content_types=['text'], state=MyStates.add_admin_check)
    dp.register_message_handler(sendAdsFunc, content_types=['text', 'photo', 'video', 'animation', 'document'],
                                state=MyStates.send_message)
    dp.register_message_handler(addMovie, content_types=['video', 'text'], state=MyStates.add_movie)

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
    dp.register_callback_query_handler(new_channel_callback, text_contains='new')
    dp.register_callback_query_handler(_100_id_callback, text_contains='-100')
