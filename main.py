import asyncio, sqlite3
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ForceReply
from env import API_TOKEN


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            second_name TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


create_table()

bot = AsyncTeleBot(API_TOKEN)


@bot.message_handler(commands=["help", "start"], func=lambda message: True)
async def welcome(message):
    await bot.send_message(
        message.chat.id,
        "Please reply to this message:",
        reply_markup=ForceReply(selective=False),
    )


@bot.message_handler(func=lambda message: message.reply_to_message is not None)
async def handle_reply(message):
    first_name, second_name = message.text.split()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (user_id, first_name, second_name) VALUES (?, ?, ?)
    """,
        (message.from_user.id, first_name, second_name),
    )
    conn.commit()
    conn.close()
    await bot.send_message(message.chat.id, f"You replied: {message.text}")


asyncio.run(bot.polling())
