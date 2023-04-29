import logging
import surrogates
import asyncio
import asyncpg

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


async def connect_to_db():
    """
    Асинхронно устанавливает соединение с базой данных.
    :return: объект подключения к базе данных.
    """
    conn = await asyncpg.connect(user='postgres', password='1234',
                                 database='postgres', host='localhost')
    return conn


async def get_categories():
    """
    Асинхронно извлекает категории мероприятий из базы данных.
    :return: список категорий в формате (id, название).
    """
    conn = await connect_to_db()
    categories = await conn.fetch("SELECT id, name FROM categories")
    await conn.close()
    return categories


# Обновление статуса категории в БД
async def update_user_interest(category_id: int, user_id: int, is_interested: bool):
    conn = await connect_to_db()
    if not is_interested:
        await conn.execute("INSERT INTO user_interest (category_id, user_id) VALUES ($1, $2)", category_id, user_id)
    else:
        await conn.execute("DELETE FROM user_interest WHERE category_id = $1 AND user_id = $2", category_id, user_id)


# Создание inline-клавиатуры с категориями
async def create_categories_keyboard(user_id: int):
    """
    Функция для создания inline-клавиатуры с категориями.
    :return: inline-клавиатура с категориями и флагами заинтересованности пользователя.
    """
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    categories = await get_categories()
    user_interests = await get_user_interests(user_id)
    for category in categories:
        is_interested = category["id"] in user_interests
        emoji = check if is_interested else cross
        button = types.InlineKeyboardButton(text=f"{category['name']} {emoji}", callback_data=f"category:{category['id']}")
        keyboard.insert(button)
    keyboard.insert(types.InlineKeyboardButton(text="save", callback_data="save"))
    return keyboard


# Получение списка категорий, которые интересны пользователю
async def get_user_interests(user_id: int):
    """
    Асинхронно получает список категорий, которые интересны пользователю из базы данных.
    :param user_id id пользователя
    :return: список категорий в формате (id, название).
    """
    conn = await connect_to_db()
    rows = await conn.fetch("SELECT category_id FROM user_interest WHERE user_id = $1", user_id)
    return [row["category_id"] for row in rows]


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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
