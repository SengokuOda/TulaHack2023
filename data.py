import asyncpg
from datetime import datetime, timedelta

async def connect_to_db():
    conn = await asyncpg.connect(user='postgres', password='1234',
                                 database='postgres', host='localhost')
    return conn


async def get_categories():
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


async def get_event_by_id(event_id: int):
    conn = await connect_to_db()
    query = "SELECT * FROM events WHERE id = $1"
    result = await conn.fetchrow(query, event_id)
    return result


async def add_reminder(event_id: int, remind_time: datetime, user_id: int):
    try:
        # Подключаемся к базе данных
        conn = await connect_to_db()

        # Создаем новое напоминание в таблице reminders
        await conn.execute("INSERT INTO reminders (event_id, user_id, reminder_time) VALUES ($1, $2, $3)",
                            event_id, user_id, remind_time)
    finally:
        # Закрываем соединение с базой данных
        await conn.close()
