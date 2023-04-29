import logging
import surrogates
import asyncio
import asyncpg
from datetime import datetime, timedelta
from data import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text


def zaglushka():
    return ['1', 'Название']


API_TOKEN = '6019862801:AAHv9nqLJdxGFVh8aSw0ZUJMQHBm4Jowamk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


# Обработчик команды /alert
@dp.message_handler(commands=['alert'])
async def alert_cmd_handler(message: types.Message):
    # Создаем inline клавиатуру
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton("Создать напоминание", web_app=types.WebAppInfo(url="https://loquacious-sunflower-bac3e6.netlify.app")),
                 types.KeyboardButton("Редактировать напоминания", callback_data="edit_reminders"))
    # Отправляем сообщение с inline клавиатурой
    await bot.send_message(chat_id=message.chat.id,
                           text="Выберите действие:",
                           reply_markup=keyboard)


@dp.message_handler(content_types="web_app_data") #получаем отправленные данные
async def answer(webAppMes):
    a = zaglushka()[0]
    await send_reminder_options(int(a), chat_id=webAppMes.chat.id)
    #print(webAppMes) #вся информация о сообщении
    #print(webAppMes.chat.id)
    #print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота


async def send_reminder_options(event_id: int, chat_id: int):
    # Получаем информацию о мероприятии из базы данных
    conn = await connect_to_db()
    event = await conn.fetchrow("SELECT event_name, start_date FROM events WHERE id = $1", event_id)

    if event:
        event_name = event['event_name']
        start_date = datetime.strptime(event['start_date'], "%d.%m.%Y %H:%M")
        text = f"Мероприятие: {event_name}\nДата и время: {start_date}\n\nВыберите время напоминания:"

        # Создаем InlineKeyboardMarkup с кнопками выбора времени
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton(text="За неделю", callback_data=f"reminder_1w_{event_id}"),
            types.InlineKeyboardButton(text="За 2 дня", callback_data=f"reminder_2d_{event_id}"),
            types.InlineKeyboardButton(text="За день", callback_data=f"reminder_1d_{event_id}"),
        )
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, "Мероприятие не найдено.")


@dp.callback_query_handler(lambda query: query.data.startswith('reminder_'))
async def process_reminder_callback(query: types.CallbackQuery):
    event_id = int(query.data.split("_")[-1])
    if query.data.startswith('reminder_1w'):
        remind_time = datetime.now() + timedelta(weeks=1)
    elif query.data.startswith('reminder_2d'):
        remind_time = datetime.now() + timedelta(days=2)
    elif query.data.startswith('reminder_1d'):
        remind_time = datetime.now() + timedelta(days=1)
    else:
        await bot.answer_callback_query(callback_query_id=query.id, text="Неизвестное время напоминания")
        return
    event = await get_event_by_id(event_id)
    text = f"Напоминание для мероприятия '{event['event_name']}' было установлено на {remind_time}"
    await add_reminder(event_id, remind_time, query.from_user.id)
    await bot.send_message(chat_id=query.from_user.id, text=text)
    await bot.answer_callback_query(callback_query_id=query.id, text="Напоминание установлено")

# на будущее
#await bot.edit_message_reply_markup()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
