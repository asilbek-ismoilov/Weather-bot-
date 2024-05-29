from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram import F
from aiogram.types import Message,InlineKeyboardButton
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filters.admin import IsBotAdminFilter
from filters.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext #new
from states.state_s import Adverts, ObHavo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from weather import get_weather
from keyboard_buttons.weather_button import havo_button, obh_button
from keyboard_buttons.weather_inl_b import weather_inl_button
import time 

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id) #foydalanuvchi bazaga qo'shildi
        await message.answer(text="Assalomu alaykum, botimizga hush kelibsiz", reply_markup=obh_button)
    except:
        await message.answer(text="Assalomu alaykum", reply_markup=obh_button)


@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)



#help commands
@dp.message(Command("help"))
async def help_commands(message:Message):
    await message.answer("Sizga qanday yordam kerak")
    text = message.text
    await bot.send_message(chat_id=ADMINS, text=text)



#about commands
@dp.message(Command("about"))
async def about_commands(message:Message):
    await message.answer("Ushbu bot orqali ob-havo haqida ma'lumot olishingiz mumkin !")


@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)


@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.01)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()

@dp.message(F.text=="Weather ⛅️")
async def get_weather_command(message: Message,state:FSMContext):
    await message.answer(text="Shahar nomini kiriting!", reply_markup=havo_button)
    await state.set_state(ObHavo.havo)

@dp.message(ObHavo.havo)
async def send_weather(message: Message, state:FSMContext):
    city = message.text
    weather = get_weather(city)
    
    Vaqt = weather.get("Vaqt", "Noma'lum")
    Harorat = weather.get("Harorat", "Noma'lum")
    Bosim = weather.get("Bosim", "Noma'lum")
    Namlik = weather.get("Namlik", "Noma'lum")
    Shamol = weather.get("Shamol", "Noma'lum")

    javob = (f"⛅️ 𝗢𝗯-𝗵𝗮𝘃𝗼 𝗺𝗮'𝗹𝘂𝗺𝗼𝘁𝗹𝗮𝗿𝗶:\n\n⏰ Vaqt : {Vaqt}\n\n🌡 Harorat : {Harorat}\n\n🌬 Bosim : {Bosim}\n\n💧 Namlik : {Namlik}\n\n💨 Shamol: {Shamol}")
    await message.answer(javob)
# 𝑶𝒃-𝒉𝒂𝒗𝒐 𝒎𝒂'𝒍𝒖𝒎𝒐𝒕𝒍𝒂𝒓𝒊
@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:

        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)


def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    from middlewares.throttling import ThrottlingMiddleware

    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))



async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    await set_default_commands(bot)
    await dp.start_polling(bot)
    setup_middlewares(dispatcher=dp, bot=bot)




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())