from loader import dp
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.havo_stt import ObHavo
from weather import get_weather
from keyboard_buttons.weather_button import havo_button
from keyboard_buttons.weather_inl_b import weather_inl_button

@dp.message(F.text=="Weather ⛅️")
async def get_weather_command(message: Message,state:FSMContext):
    await message.answer(text="Shaharni tanlang !", reply_markup=weather_inl_button) # reply_markup=havo_button, 
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
