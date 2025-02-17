from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import db

bot = None


async def welcome(message):
    """Handle /start command"""
    if not user_exists(message.from_user.id):
        db.query_data(
            "INSERT INTO users (user_id, role) VALUES (?, 'user')",
            (message.from_user.id,),
        )
    await start_registration(message)


async def message_handler(message):
    """Entry point for all messages"""
    if not user_exists(message.from_user.id):
        await welcome(message)
        return

    # If user is in middle of registration, continue with last step


async def callback_query_handler(call):
    """Handle inline keyboard interactions"""
    try:
        if call.data == "name confirmed":
            await ask_surname(call)
        elif call.data == "name rejected":
            await handle_name_rejection(call)
    finally:
        await bot.answer_callback_query(call.id)


async def start_registration(message):
    """Begin registration process"""
    await bot.send_message(
        message.chat.id, "Привет! Для регистрации укажи свои данные."
    )
    await ask_name(message)


async def ask_name(message):
    """Request name"""
    msg = await bot.send_message(message.chat.id, "Напиши своё имя:")
    await bot.register_next_step_handler(msg, process_name)


async def process_name(message):
    """Handle name input"""
    db.query_data(
        "UPDATE users SET first_name = ? WHERE user_id = ?",
        (message.text, message.from_user.id),
    )
    await confirm_name(message)


async def confirm_name(message):
    """Confirm name with inline keyboard"""
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Да", callback_data="name confirmed"),
        InlineKeyboardButton("Нет", callback_data="name rejected"),
    )
    await bot.send_message(
        message.chat.id,
        f"Вы уверены, что ваше имя {message.text}?",
        reply_markup=markup,
    )


async def ask_surname(call):
    """Process confirmed name"""
    msg = await bot.send_message(
        call.message.chat.id, "Прекрасно! Теперь напиши свою фамилию:"
    )
    await bot.register_next_step_handler(msg, process_surname)


async def handle_name_rejection(call):
    """Restart name entry"""
    await ask_name(call.message)


async def process_surname(message):
    """Handle surname input"""
    db.query_data(
        "UPDATE users SET second_name = ? WHERE user_id = ?",
        (message.text, message.from_user.id),
    )
    await confirm_surname(message)


async def confirm_surname(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Да", callback_data="surname confirmed"),
        InlineKeyboardButton("Нет", callback_data="surname rejected"),
    )
    await bot.send_message(
        message.chat.id,
        f"Вы уверены, что ваше имя {message.text}?",
        reply_markup=markup,
    )


async def handle_surname_confirmation(call):
    """Process confirmed name"""
    msg = await bot.send_message(
        call.message.chat.id, "Прекрасно! Теперь выбери свой пол:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("М", callback_data="male"),
        InlineKeyboardButton("Ж", callback_data="female"),
    )
    await bot.send_message(call.message.chat.id, "Выберите свой пол:", markup=markup)


async def handle_surname_rejection(call):
    """Restart name entry"""
    await ask_surname(call.message)


async def finish_registration(message):
    """Finalize registration"""
    await bot.send_message(message.chat.id, "Спасибо! Регистрация завершена.")
