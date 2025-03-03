import asyncio
from telebot.async_telebot import AsyncTeleBot
from env import API_TOKEN
import message_handlers


bot = AsyncTeleBot(API_TOKEN)

message_handlers.bot = bot

# Register command handlers first
bot.register_message_handler(message_handlers.get_competitions, commands=["competitions"])
bot.register_message_handler(message_handlers.my_competitions, commands=["my_competitions"])
# Register the generic message handler last
bot.register_message_handler(message_handlers.message_handler, func=lambda message: True)

# Register callback query handler
bot.register_callback_query_handler(message_handlers.callback_query_handler, lambda call: True)

asyncio.run(bot.polling())
