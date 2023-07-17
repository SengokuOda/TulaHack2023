import logging
import surrogates

from remind_module import *
from typing import Union
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from data import get_categories, get_user_interests, update_user_interest
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text


API_TOKEN = '6019862801:AAHv9nqLJdxGFVh8aSw0ZUJMQHBm4Jowamk'

logging.basicConfig(level=logging.INFO)

cross = surrogates.decode('\u274C')
check = surrogates.decode('\u2705')

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

kb = [[
    types.KeyboardButton(text="Хочу куда-то сходить"),
    types.KeyboardButton(text="Хочу организовать")
],     # any
]


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=True)
    await message.answer("Я - бот-помощник в поиске мероприятий, с помощью меня Вы можете найти для себя что-то интересное в нашем славном городе, либо организовать своё", reply_markup=keyboard)


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
    keyboard.insert(types.InlineKeyboardButton(text="СОХРАНИТЬ", callback_data="save"))
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


@dp.message_handler(Text(equals="Хочу куда-то сходить"))
# логика user
async def if_user(message: types.Message):
    user_id = message.from_user.id
    inline_keyboard = await create_categories_keyboard(user_id=user_id)
    await message.answer(text="Выберите категории, которые вам интересны", reply_markup=inline_keyboard)


@dp.callback_query_handler(text="save")
async def animation_handler(query: types.CallbackQuery):
    for i in range(0, 110, 10):
        await query.message.edit_text(text=f"{i}%")
        if i == 100:
            await query.message.edit_text(text="100%\nИзменения успешно сохранены!")
            await create_user_keyboard(query.from_user.id)


class EventRegistrationForm(StatesGroup):
    fio = State()
    location = State()
    date_time = State()
    payment_link = State()
    age_limit = State()


@dp.message_handler(Text(equals='Хочу организовать'))
async def cmd_register(message: types.Message):
    await message.answer("Для регистрации мероприятия необходимо заполнить форму.\nВведите ваше ФИО:")
    await EventRegistrationForm.fio.set()


@dp.message_handler(state=EventRegistrationForm.fio)
async def process_fio(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text
    await message.answer("Введите местоположение мероприятия:")
    await EventRegistrationForm.location.set()


@dp.message_handler(state=EventRegistrationForm.location, content_types=[types.ContentType.VENUE, types.ContentType.LOCATION])
async def process_location(message: Union[types.Location, types.Venue], state: FSMContext):
    try:
        coordinates = None
        longitude = message.location.longitude
        latitude = message.location.latitude
        coordinates = (longitude, latitude)
        async with state.proxy() as data:
            data['coordinates'] = coordinates
        await message.answer("Введите дату и время начала мероприятия (формат: дд.мм.гггг чч:мм):")
        await EventRegistrationForm.date_time.set()
    except:
        await message.answer("Неверный формат. Пожалуйста, отправьте свою локацию или местоположение мероприятия.")


@dp.message_handler(state=EventRegistrationForm.date_time)
async def process_date_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_time'] = message.text
    await message.answer("Является ли мероприятие платным? (да/нет)")
    await EventRegistrationForm.next()


@dp.message_handler(lambda message: message.text.lower() in ["да", "нет"], state=EventRegistrationForm.payment_link)
async def process_payment_link_yes_no(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == "да":
            data["is_payment"] = True
            await message.answer("Введите ссылку на оплату:")
            await EventRegistrationForm.payment_link.set()
        elif message.text.lower() == "нет":
            data["is_payment"] = False
            await message.answer("Введите возрастное ограничение:")
            await EventRegistrationForm.age_limit.set()


@dp.message_handler(state=EventRegistrationForm.payment_link)
async def process_payment_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['payment_link'] = message.text
    await message.answer("Введите возрастное ограничение:")
    await EventRegistrationForm.age_limit.set()


@dp.message_handler(state=EventRegistrationForm.age_limit)
async def process_age_limit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age_limit'] = message.text
    await state.finish()
    await message.answer("Регистрация мероприятия завершена.")









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




# Обработчик команды /alert
@dp.message_handler(commands=['alert'])
async def alert_cmd_handler(message: types.Message):
    # Создаем inline клавиатуру
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Выбрать мероприятие", web_app=types.WebAppInfo(url="https://loquacious-sunflower-bac3e6.netlify.app/")),
                 types.KeyboardButton("Редактировать напоминания"))
    # Отправляем сообщение с inline клавиатурой
    await bot.send_message(chat_id=message.chat.id,
                           text="Выберите действие:",
                           reply_markup=keyboard)



# выбрать из предыдущих
@dp.message_handler(content_types=types.ContentTypes.VENUE) #получаем отправленные данные
async def check_loc(location_message: types.Location):
    longitude = location_message.longitude
    latitude = location_message.latitude
    # сохраняем координаты в переменную
    coordinates = (longitude, latitude)

# выбрать точку на карте
@dp.message_handler(content_types=types.ContentTypes.LOCATION) #получаем отправленные данные
async def check_loc(location_message: types.Location):
    longitude = location_message.longitude
    latitude = location_message.latitude
    # сохраняем координаты в переменную
    coordinates = (longitude, latitude)


@dp.message_handler(content_types="web_app_data") #получаем отправленные данные
async def answer(webAppMes):
    json_str = json.loads(webAppMes.web_app_data.data)
    event = {'event_name': json_str['event_name'], 'start_date': json_str['start_date'], 'address': json_str['address']}
    await send_reminder_options(json_str['id'], chat_id=webAppMes.chat.id, event=event)
    print(webAppMes) #вся информация о сообщении
    print(webAppMes.chat.id)
    print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота


# ТЕСТ
@dp.message_handler(Text(equals="Редактировать напоминания"))
async def test(query: types.Message):
    a = 1
    await handle_location_request(message=query.text)


# Функция для проверки времени напоминания
async def check_reminders():
    while True:
        # Получаем текущее время
        now = datetime.now()
        conn = await connect_to_db()
        # Выбираем из базы данных пользователей, у которых время напоминания равно текущему времени
        rows = await conn.fetch(f"SELECT user_id, reminder_time FROM reminders WHERE reminder_time <'{now}'")
        for row in rows:
            user_id = row[0]
            reminder_time = row[1]
            await send_reminder(user_id)
            await conn.execute(f"DELETE FROM reminders WHERE reminder_time < '{now}'")

        # Ждем 1 секунду перед следующей проверкой
        await asyncio.sleep(1)


# Функция для отправки напоминания (дописать напоминание чего)
async def send_reminder(user_id):
    try:
        # Отправляем сообщение пользователю
        await bot.send_message(chat_id=user_id, text="Напоминание!")
    except exceptions.BotBlocked:
        print(f"Бот заблокирован пользователем {user_id}")
    except exceptions.ChatNotFound:
        print(f"Чат не найден, chat_id={user_id}")


async def send_reminder_options(event_id: int, chat_id: int, event: dict):
    # Получаем информацию о мероприятии из базы данных
    conn = await connect_to_db()
    event_2 = await conn.fetchrow("SELECT event_name, start_date FROM events WHERE id = $1", event_id)
    if event:
        event_name = event['event_name']
        #start_date = datetime.strptime(event_2['start_date'], "%d.%m.%Y %H:%M")
        start_date = datetime.fromisoformat(event['start_date'].replace('T', ' '))
        text = f"Мероприятие: {event_name}\nДата и время: {start_date}\n\nВыберите время напоминания:"

        # Создаем InlineKeyboardMarkup с кнопками выбора времени
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton(text="За 2 дня", callback_data=f"reminder_2d_{event_id}"),
            types.InlineKeyboardButton(text="За 1 день", callback_data=f"reminder_1d_{event_id}"),
            types.InlineKeyboardButton(text="За 1 час", callback_data=f"reminder_1h_{event_id}"),
        )
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, "Мероприятие не найдено.")


@dp.callback_query_handler(lambda query: query.data.startswith('reminder_'))
async def process_reminder_callback(query: types.CallbackQuery):
    event_id = int(query.data.split("_")[-1])
    event = await get_event_by_id(event_id)
    start_date = datetime.fromisoformat(event['start_date'].replace('T', ' '))
    if query.data.startswith('reminder_2d'):
        remind_time = start_date - timedelta(days=2)
    elif query.data.startswith('reminder_1d'):
        remind_time = start_date - timedelta(days=1)
    elif query.data.startswith('reminder_1h'):
        remind_time = start_date - timedelta(hours=1)
    else:
        await bot.answer_callback_query(callback_query_id=query.id, text="Неизвестное время напоминания")
        return
    text = f"Напоминание для мероприятия '{event['event_name']}' было установлено на {remind_time}"
    await add_reminder(event_id, remind_time, query.from_user.id)
    await bot.send_message(chat_id=query.from_user.id, text=text)
    await bot.answer_callback_query(callback_query_id=query.id, text="Напоминание установлено")




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)/te
