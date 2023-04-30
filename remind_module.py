import logging
import surrogates
import asyncio
import asyncpg
from aiogram import exceptions
import json
from datetime import datetime, timedelta
from data import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils import callback_data


API_TOKEN = '6019862801:AAHv9nqLJdxGFVh8aSw0ZUJMQHBm4Jowamk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

async def create_user_keyboard(user_id):
    # Создание клавиатуры
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    conn = await connect_to_db()

    reminders = await conn.fetch(f"SELECT * FROM reminders WHERE user_id={user_id}")
    #Добавление кнопок напоминаний
    for reminder in reminders:
        reminder_text = f"Напоминание {reminder[0]}"
        callback_data = f"reminder_{reminder[0]}"
        keyboard.insert(types.InlineKeyboardButton(reminder_text, callback_data=callback_data))

    # Добавление кнопок навигации
    current_index = 0
    current_text = f"Напоминание {reminders[current_index][0]}"
    back_button = types.InlineKeyboardButton("⬅️ Назад", callback_data="back")
    forward_button = types.InlineKeyboardButton("➡️ Вперед", callback_data="forward")
    delete_button = types.InlineKeyboardButton("❌ Удалить", callback_data="delete")
    keyboard.insert(delete_button)

    return keyboard


@dp.message_handler(commands=['test_nav1'])
async def redact_alerts(message: types.Message):
    keyboard = await create_user_keyboard(message.from_user.id)
    await message.answer("Навигация 1", reply_markup=keyboard)
    # отправляем сообщение с инлайн-клавиатурой

# на будущее
#await bot.edit_message_reply_markup()
async def main():
    await check_reminders()




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)
