from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime
import db

bot = None

# misc db queries


def user_exists(chat_id):
    print("count", db.query_data("SELECT COUNT(*) > 0 FROM users WHERE chat_id = ?", (chat_id,))[0][0])
    if db.query_data("SELECT COUNT(*) > 0 FROM users WHERE chat_id = ?", (chat_id,))[0][0]:
        print("yes")
    return db.query_data("SELECT COUNT(*) > 0 FROM users WHERE chat_id = ?", (chat_id,))[0][0]


def get_user_state(chat_id):
    result = db.query_data("SELECT state FROM users WHERE chat_id = ?", (chat_id,))
    return result[0][0] if result else None


# entry point for all mesagess


async def message_handler(message):
    """Entry point for all messages"""
    chat_id = message.chat.id
    if not user_exists(chat_id):
        await welcome(message)
        return

    state = get_user_state(chat_id)

    if state == "name":
        await process_name(message)
    elif state == "surname":
        await process_surname(message)
    elif state == "gender":
        await bot.send_message(message.chat.id, "Пожалуйста, выберите пол используя кнопки выше.")
    elif state in ["confirm_name", "confirm_surname"]:
        await bot.send_message(
            message.chat.id,
            "Пожалуйста, подтвердите текущий шаг используя кнопки выше.",
        )
    elif state == "choosing competition":
        await competition_chosen(message)
    elif state == "seeing competitions":
        await competition_seen(message)
    else:
        await help(message)


async def help(message):
    role = db.query_data("select role from users where chat_id = ?", (message.chat.id,))[0][0]
    if role == "user":
        await bot.send_message(
            message.chat.id,
            """
Чтобы посмотреть доступные соревнования и зарегистрироваться на них, введите команду /competitions 
Чтобы посмотреть соревнования, на которые вы записались, и снять свою регистрацию, введите /my_competitions
        """,
        )
    if role == "admin":
        await bot.send_message(
            message.chat.id,
            """
Чтобы посмотреть доступные соревнования и зарегистрироваться на них, введите команду /competitions 
Чтобы посмотреть соревнования, на которые вы записались, и снять свою регистрацию, введите /my_competitions
Чтобы создaть соревнование, введите команду /new_competition 
        """,
        )


# entry point for callback queries


async def callback_query_handler(call):
    """Handle inline keyboard interactions"""
    try:
        chat_id = call.from_user.id
        if call.data == "name confirmed":
            db.query_data("UPDATE users SET state = 'surname' WHERE chat_id = ?", (chat_id,))
            await ask_surname(call)
        elif call.data == "name rejected":
            db.query_data("UPDATE users SET state = 'name' WHERE chat_id = ?", (chat_id,))
            await handle_name_rejection(call)
        elif call.data == "surname confirmed":
            db.query_data("UPDATE users SET state = 'gender' WHERE chat_id = ?", (chat_id,))
            await ask_gender(call)
        elif call.data == "surname rejected":
            db.query_data("UPDATE users SET state = 'surname' WHERE chat_id = ?", (chat_id,))
            await handle_surname_rejection(call)
        elif call.data == "male":
            await handle_male(call)
        elif call.data == "female":
            await handle_female(call)
    finally:
        await bot.answer_callback_query(call.id)


# registration


async def welcome(message):
    """Handle /start command"""
    if not user_exists(message.chat.id):
        db.query_data(
            "INSERT INTO users (chat_id, role, state) VALUES (?, 'user', 'name')",
            (message.chat.id,),
        )
    await start_registration(message)


async def start_registration(message):
    """Begin registration process"""
    await bot.send_message(message.chat.id, "Привет! Для регистрации укажи свои данные.")
    await ask_name(message)


async def ask_name(message):
    """Request name"""
    db.query_data("UPDATE users SET state = 'name' WHERE chat_id = ?", (message.chat.id,))
    await bot.send_message(message.chat.id, "Напиши своё имя:")


async def process_name(message):
    """Handle name input"""
    db.query_data(
        "UPDATE users SET first_name = ?, state = 'confirm_name' WHERE chat_id = ?",
        (message.text, message.chat.id),
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

    await bot.send_message(call.message.chat.id, "Прекрасно! Теперь напиши свою фамилию:")


async def handle_name_rejection(call):
    """Restart name entry"""
    await bot.send_message(call.message.chat.id, "Пожалуйста, введите ваше имя снова:")


async def process_surname(message):
    """Handle surname input"""
    db.query_data(
        "UPDATE users SET second_name = ?, state = 'confirm_surname' WHERE chat_id = ?",
        (message.text, message.chat.id),
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
        f"Вы уверены, что ваша фамилия {message.text}?",
        reply_markup=markup,
    )


async def ask_gender(call):
    """Ask for gender selection"""
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("М", callback_data="male"),
        InlineKeyboardButton("Ж", callback_data="female"),
    )
    await bot.send_message(call.message.chat.id, "Выберите свой пол:", reply_markup=markup)


async def handle_surname_rejection(call):
    """Restart surname entry"""
    await bot.send_message(call.message.chat.id, "Пожалуйста, введите вашу фамилию снова:")


async def handle_male(call):
    db.query_data(
        "UPDATE users SET gender = 'М', state = 'complete' WHERE chat_id = ?",
        (call.from_user.id,),
    )
    await bot.send_message(
        call.message.chat.id,
        "Регистрация завершена! Для просмотра доступных команд введите /start",
    )


async def handle_female(call):
    db.query_data(
        "UPDATE users SET gender = 'Ж', state = 'complete' WHERE chat_id = ?",
        (call.from_user.id,),
    )
    await bot.send_message(
        call.message.chat.id,
        "Регистрация завершена! Для просмотра доступных команд введите /start",
    )


# typical user interactions


def format_competition(competition):
    # Try to parse using ISO 8601 format
    try:
        dt = datetime.fromisoformat(competition[2])
    except ValueError:
        # Fallback if the format is different
        dt = datetime.strptime(competition[2], "%Y-%m-%d %H:%M:%S")

    already_participating_result = db.query_data(
        "SELECT COUNT(*) FROM registrations WHERE competition_id = ?", (competition[0],)
    )
    already_participating = already_participating_result[0][0] if already_participating_result else 0
    return f"""
Номер соревнования: {competition[0]}
{competition[1]}
дата - {dt.day:02}.{dt.month:02}.{dt.year} {dt.hour:02}:{dt.minute:02}
Зарегестрировано {already_participating}/{competition[4]}
    """


async def get_competitions(message):
    user_gender_result = db.query_data("SELECT gender FROM users WHERE chat_id = ?", (message.chat.id,))

    if not user_gender_result:
        await bot.send_message(message.chat.id, "User not found.")
        return

    user_gender = user_gender_result[0][0]  # Assuming the result is a list of tuples

    competitions = db.query_data(
        """SELECT * FROM competitions WHERE datetime(date) > datetime('now') 
        AND gender = ?""",
        (user_gender,),
    )

    if not competitions:
        await bot.send_message(message.chat.id, "No upcoming competitions found.")
        return

    competition_ids = []

    for competition in competitions:
        competition_ids.append(str(competition[0]))
        competition_message = format_competition(competition)
        await bot.send_message(message.chat.id, competition_message)

    db.query_data(
        "UPDATE users SET state = 'choosing competition' WHERE chat_id = ?",
        (message.chat.id,),
    )
    markup = ReplyKeyboardMarkup()
    markup.add(*competition_ids, "Выйти")

    await bot.send_message(
        message.chat.id,
        "Что бы зарегистрироваться на соревнование, нажмите на кнопку с номером этого соревнования. Чтобы выйти из этого меню, нажмите 'Выйти'",
        reply_markup=markup,
    )


async def my_competitions(message):
    competitions = db.query_data(
        """SELECT * FROM competitions WHERE date > datetime('now') 
        AND id IN 
        (SELECT competition_id FROM registrations WHERE chat_id = ?);""",
        (message.chat.id,),
    )

    if not competitions:
        await bot.send_message(message.chat.id, "Вы пока что не зарегестрированы ни на какие соревнования.")

    db.query_data("UPDATE users SET state = 'seeing competitions' WHERE chat_id = ?", (message.chat.id,))

    competition_ids = []

    for competition in competitions:
        competition_ids.append(str(competition[0]))
        competition_message = format_competition(competition)
        await bot.send_message(message.chat.id, competition_message)

    markup = ReplyKeyboardMarkup()
    markup.add(*competition_ids, "Выйти")

    await bot.send_message(
        message.chat.id,
        "Что бы снять свою регистрацию на сорвенования, нажмите на соответствующий номер соревнования.\nЧто бы выйти в главное меню, нажмите 'Выйти'",
        reply_markup=markup,
    )


async def competition_chosen(message):
    if message.text == "Выйти":
        db.query_data("UPDATE users SET state = 'complete' WHERE chat_id = ?", (message.chat.id,))
        await bot.send_message(
            message.chat.id,
            "Вы вышли в главное меню",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        competition_ids = [i[0] for i in db.query_data("SELECT id FROM competitions")]
        try:
            test = int(message.text)
        except BaseException:
            await bot.send_message(message.chat.id, "Вы выбрали недействительный вариант.")
            return
        if int(message.text) in competition_ids:
            registered_comps = [
                i[0]
                for i in db.query_data(
                    "SELECT competition_id FROM registrations WHERE chat_id = ?",
                    (message.chat.id,),
                )
            ]
            if int(message.text) in registered_comps:
                await bot.send_message(message.chat.id, "Вы уже зарегистрированы на это соревнование.")
            else:
                db.query_data(
                    "INSERT INTO registrations(chat_id, competition_id) VALUES(?, ?)",
                    (message.chat.id, int(message.text)),
                )
                db.query_data(
                    "INSERT INTO logs(chat_id, object_id, action_type, date) VALUES(?, ?, 'registered on to a competition', datetime('now'))",
                    (message.chat.id, int(message.text)),
                )
                await bot.send_message(
                    message.chat.id,
                    f"Вы успешно зарегистрировались на соревнование номер {int(message.text)}.",
                )
        else:
            await bot.send_message(message.chat.id, "Вы выбрали недействительный вариант.")


async def competition_seen(message):
    if message.text == "Выйти":
        db.query_data("UPDATE users SET state = 'complete' WHERE chat_id = ?", (message.chat.id,))
        await bot.send_message(
            message.chat.id,
            "Вы вышли в главное меню",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        competition_ids = [i[0] for i in db.query_data("SELECT id FROM competitions")]
        try:
            test = int(message.text)
        except BaseException:
            await bot.send_message(message.chat.id, "Вы выбрали недействительный вариант.")
            return
        competition_ids = [
            i[0]
            for i in db.query_data("SELECT competition_id FROM registrations WHERE chat_id = ?", (message.chat.id,))
        ]
        if int(message.text) not in competition_ids:
            await bot.send_message(message.chat.id, "Недействительный вариант ответа")
        else:
            db.query_data(
                "DELETE FROM registrations WHERE chat_id = ? and competition_id = ?",
                (message.chat.id, int(message.text)),
            )
            await bot.send_message(message.chat.id, f"Вы больше не учавствуете в соревновании номер {message.text}")


# Admin interactions
