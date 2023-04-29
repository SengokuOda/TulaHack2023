import logging
import surrogates
import asyncio
import asyncpg

from data import connect_to_db, get_categories, get_user_interests, update_user_interest
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text


API_TOKEN = '6019862801:AAHv9nqLJdxGFVh8aSw0ZUJMQHBm4Jowamk'

logging.basicConfig(level=logging.INFO)

cross = surrogates.decode('\u274C')
check = surrogates.decode('\u2705')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

kb = [[
    types.KeyboardButton(text="Я ищу"),
    types.KeyboardButton(text="Я орг")
],     # any
]


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=True)
    await message.answer("КТО ТЫ?", reply_markup=keyboard)


# Создание inline-клавиатуры с категориями
async def create_categories_keyboard(user_id: int):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    categories = await get_categories()
    user_interests = await get_user_interests(user_id)
    for category in categories:
        is_interested = category["id"] in user_interests
        emoji = check if is_interested else cross
        button = types.InlineKeyboardButton(text=f"{category['name']} {emoji}", callback_data=f"category:{category['id']}")
        keyboard.insert(button)
    keyboard.insert(types.InlineKeyboardButton(text="save", callback_data="save"))
    return keyboard


# Обработка нажатия на кнопку
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("category:"))
async def process_callback_category(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split(":")[1])
    user_id = callback_query.from_user.id
    is_interested = category_id in await get_user_interests(user_id=user_id)
    await update_user_interest(category_id, user_id, is_interested)
    keyboard = await create_categories_keyboard(user_id)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback_query.message.message_id,
                                        reply_markup=keyboard)


@dp.message_handler(Text(equals="Я ищу"))
# логика user
async def if_user(message: types.Message):
    user_id = message.from_user.id
    inline_keyboard = await create_categories_keyboard(user_id=user_id)
    await message.answer(text="Выберите категории", reply_markup=inline_keyboard)


@dp.message_handler(Text(equals="Я орг"))
# логика org
async def if_org(message: types.Message):
    await message.reply("Он орг!")


@dp.callback_query_handler(text="save")
async def animation_handler(query: types.CallbackQuery):
    for i in range(0, 110, 10):
        await query.message.edit_text(text=f"{i}%")
        if i == 100:
            await query.message.edit_text(text="100%\nИзменения успешно сохранены!")


# Обработчик команды /alert
@dp.message_handler(Text(equals="Я орг"))
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
    a = zaglushk()[0]
   #print(webAppMes) #вся информация о сообщении
   #print(webAppMes.chat.id)
   #print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
