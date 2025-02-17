import asyncio
from telebot.async_telebot import AsyncTeleBot
from env import API_TOKEN
import message_handlers


bot = AsyncTeleBot(API_TOKEN)

message_handlers.bot = bot

bot.register_message_handler(message_handlers.welcome, commands=["/start", "/help"])
bot.register_message_handler(
    message_handlers.message_handler, func=lambda message: True
)
bot.register_callback_query_handler(
    message_handlers.callback_query_handler, lambda call: True
)

asyncio.run(bot.polling())
