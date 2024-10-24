import re  # For parsing input text
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.error import BadRequest, NetworkError
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


load_dotenv(dotenv_path=".env")
dev_chat_id = str(os.getenv("DEV_CHAT"))
telegram_token = str(os.getenv("BOT_TOKEN"))

USERNAME, FULL_NAME, JUST_NAME, GROUP, FACULTY, REGULARITY, DEPARTMENTS, BIRTH, EXPERIENCE, MOTIVATION, ACCEPT, CONFIRM = range(12)

ordinary_commands=[("start", "Запускає бота"),("help", "Коротка довідка"),("chat_id", "Показує ID цього чату"),("join", "Заповнення форми для приєднання")]
form_commands=[("cancel","Скасувати заповнення форми")]

forms={}

# if os.path.exists('forwarded.txt'):  # перевірка існування файлу forwarded.txt
#     with open('forwarded.txt', 'r+') as file1:  # зчитування із файлу у словник forwarded_messages
#         for line in file1:
#             key, values = line.strip().split(':')
#             forwarded_messages[int(key)] = list(map(int, values.split(',')))  # структуроване зчитування
# if os.path.exists('tickets.txt'):  # перевірка існування файлу tickets.txt
#     with open('tickets.txt', 'r+') as file2:  # зчитування із файлу у словник tickets
#         for line in file2:
#             key, value = line.strip().split(':')  # структуроване зчитування
#             tickets[int(key)] = str(value)
# if os.path.exists('banned.txt'):  # перевірка існування файлу banned.txt
#     with open('banned.txt', 'r+') as file3:  # зчитування із файлу у масив tickets
#         banned_users = [line.strip() for line in file3]  # структуроване зчитування

def is_valid_date(date_string: str) -> bool:
    try:
        date = datetime.strptime(date_string, "%d.%m.%Y")
        if datetime(1900, 1, 1) <= date <= datetime.now():
            return True
        else:
            return False
    except ValueError:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != dev_chat_id:
        await update.message.reply_text("Привіт. Я їжак:)")
    else:
        await context.bot.send_message(chat_id=dev_chat_id, text="У службовому чаті ця команда нічого не робить.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != dev_chat_id:
        await update.message.reply_text("Не допомагаю поки.")
    else:
        await context.bot.send_message(chat_id=dev_chat_id, text="Списку команд ще немає.")

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"ID цього чату: {update.message.chat_id}")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.set_my_commands(form_commands,scope=telegram.BotCommandScopeChat(update.message.chat_id))
    context.user_data['index']=1
    await update.message.reply_text(
        "Для заповнення форми дайте відповіді на запитання нижче(для скасування заповнення форми введіть /cancel).")
    username = update.message.from_user.username if update.message.from_user.username else ""
    if(username==""):
        await update.message.reply_text(f"{context.user_data.get('index')}. Ваш telegram username. У форматі @my_username.")
        return USERNAME
    else:
        context.user_data['username'] = (f"@{username}").replace("_","\_")
        await update.message.reply_text(f"{context.user_data.get('index')}. ПІБ(повністю без скорочень):")
        return FULL_NAME


async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text.replace("_","\_")
    index = context.user_data.get('index')
    context.user_data['index'] = index+1
    await update.message.reply_text(f"{context.user_data.get('index')}. Як до Вас звертатись?")
    return FULL_NAME

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pattern = r'^[\u0400-\u04FF]+$'
    if not re.match(pattern, update.message.text):
        await update.message.reply_text("Це поле може містити лише літери української абетки. Введіть ще раз, будь ласка.")
        return FULL_NAME
    else:
        context.user_data['full_name'] = update.message.text
        index = context.user_data.get('index')
        context.user_data['index'] = index + 1
        await update.message.reply_text(f"{context.user_data.get('index')}. Як до Вас звертатись?")
        return JUST_NAME

async def just_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['just_name'] = update.message.text
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await update.message.reply_text(f"{context.user_data.get('index')}. Абревіатура вашого факультету/інституту? Українською у форматі АБВ.")
    return FACULTY


async def faculty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pattern = r'^[\u0400-\u04FF]+$'
    if not re.match(pattern, update.message.text):
        await update.message.reply_text("Це поле може містити лише літери української абетки. Введіть ще раз, будь ласка.")
        return FACULTY
    else:
        context.user_data['faculty'] = update.message.text
        index = context.user_data.get('index')
        context.user_data['index'] = index + 1
        await update.message.reply_text(f"{context.user_data.get('index')}. Шифр вашої групи? Українською у форматі ХХ-00.")
        return GROUP


async def group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pattern = r'^[\u0400-\u04FF]{2}-\d{2}$'
    if not re.match(pattern, update.message.text):
        await update.message.reply_text("Невірний формат введення даних. Введіть ще раз, будь ласка.")
        return GROUP
    else:
        context.user_data['group'] = update.message.text
        keyboard = [
            [InlineKeyboardButton("Легко можу приїхати на КПІ або часто там буваю", callback_data="Так, можу часто")],
            [InlineKeyboardButton("Не часто зможу бути на КПІ", callback_data="Зможу, але не часто")],
            [InlineKeyboardButton("Працюватиму лише дистанційно", callback_data="Лише дистанційно")],
        ]
        index = context.user_data.get('index')
        context.user_data['index'] = index + 1
        await update.message.reply_text(f"{context.user_data.get('index')}. Як часто Ви буваєте на КПІ? Розуміти місцезнаходження команди важливо для планування заходів.", reply_markup=InlineKeyboardMarkup(keyboard))
        return REGULARITY

async def regularity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    departments = [
        ("ІТ-служба", "ІТ-служба"),
        ("Служба господарської роботи", "Служба господарської роботи"),
        ("Служба студентських об’єднань", "Служба студентських об’єднань"),
        ("Служба зовнішніх зв’язків", "Служба зовнішніх зв’язків"),
        ("Служба локальних зв’язків", "Служба локальних зв’язків"),
        ("Секретаріат", "Секретаріат"),
        ("Департамент медіа", "Департамент медіа"),
        ("Департамент профорієнтації", "Департамент профорієнтації"),
        ("Департамент аналітики", "Департамент аналітики"),
        ("Проєктний департамент", "Проєктний департамент")
    ]
    query = update.callback_query
    await query.answer()
    context.user_data['regularity'] = query.data
    context.user_data['departments'] = departments
    context.user_data['choice1'] = "0"
    if(query.data=="Так, можу часто"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Так, можу часто 🔘 ", callback_data="none")],
        ]
    elif(query.data=="Зможу, але не часто"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Зможу, але не часто 🔘 ", callback_data="none")],
        ]
    elif(query.data=="Лише дистанційно"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Лише дистанційно 🔘 ", callback_data="none")],
        ]
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(none_keyboard))
    keyboard = [[InlineKeyboardButton(text, callback_data=callback)] for text, callback in departments]
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await query.message.reply_text(f"{context.user_data.get('index')}. Почитайте [статтю](https://www.hashtap.com/@sr\\_kpi/%D1%81%D1%82%D1%83%D0%B4%D0%B5%D0%BD%D1%82%D1%81%D1%8C%D0%BA%D0%B0-%D1%80%D0%B0%D0%B4%D0%B0-%D0%BA%D0%BF%D1%96-Zdg3640XZLl6) про підрозділи Студради КПІ.\n"
                                   "Оберіть не більше 2 департаментів/служб нижче.",reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return DEPARTMENTS


async def departments_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    departments = context.user_data.get('departments')
    if(query.data=="none"):
        return DEPARTMENTS
    else:
        if(context.user_data.get('choice1')=="0"):
            new_button = ("Завершити вибір➡️","11")
            context.user_data['choice1'] = query.data
            for i, (name, id) in enumerate(departments):
                if name == query.data:
                    departments[i] = (f"🔘 {query.data} 🔘 ","none")
                    break
            departments.append(new_button)
            context.user_data['departments'] = departments
            keyboard = [[InlineKeyboardButton(text, callback_data=callback)] for text, callback in departments]
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            return DEPARTMENTS
        else:
            if(query.data=="11"):
                context.user_data['choice2'] = " "
                buff_choice = context.user_data.get('choice1')
                no_delete_item = (f"🔘 {buff_choice} 🔘 ","none")
                departments = [item for item in departments if item == no_delete_item]
                keyboard = [[InlineKeyboardButton(text, callback_data=callback)] for text, callback in departments]
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                context.user_data['choice2'] = f", {query.data}"
                for i, (name, id) in enumerate(departments):
                    if name == query.data:
                        departments[i] = (f"🔘 {query.data} 🔘 ", "none")
                        break
                buff_choice = context.user_data.get('choice1')
                no_delete_items = [(f"🔘 {buff_choice} 🔘 ", "none"),(f"🔘 {query.data} 🔘 ", "none")]
                departments = [item for item in departments if item in no_delete_items]
                keyboard = [[InlineKeyboardButton(text, callback_data=callback)] for text, callback in departments]
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await query.message.reply_text(f"{context.user_data.get('index')}. Ваша дата народження? Формат дд.мм.рррр.")
    return BIRTH


async def birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if(is_valid_date(update.message.text)):
        context.user_data['birthdate'] = update.message.text
        index = context.user_data.get('index')
        context.user_data['index'] = index + 1
        await update.message.reply_text(f"{context.user_data.get('index')}. Чи був у Вас досвід у волонтерстві раніше?\nРозкажіть тут про будь-який Ваш досвід волонтерства та організації проектів.")
        return EXPERIENCE
    else:
        await update.message.reply_text("Невірний формат введення даних або дата. Введіть ще раз, будь ласка.")
        return BIRTH


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['experience'] = update.message.text
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await update.message.reply_text(
        f"{context.user_data.get('index')}. Ваша мотивація бути в команді Студради КПІ."
        " Напишіть, чому хочете доєднатись до Студради.\nБудь ласка, розпишіть кількома реченнями.")
    return MOTIVATION


async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['motivation'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Так, даю свою згоду✅", callback_data="1")],
        [InlineKeyboardButton("Ні, скасувати заповнення форми❌", callback_data="-1")],
    ]
    index = context.user_data.get('index')
    context.user_data['index'] = index + 1
    await update.message.reply_text(f"{context.user_data.get('index')}. Даєте свою згоду на обробку персональних даних?",reply_markup=InlineKeyboardMarkup(keyboard))
    return ACCEPT


async def acceptance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if (query.data == "none"):
        return ACCEPT
    else:
        if(query.data=="1"):
            keyboard = [[InlineKeyboardButton("🔘 Так, даю свою згоду✅ 🔘 ", callback_data="none")]]
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            keyboard = [
                [InlineKeyboardButton("Все вірно, надіслати", callback_data="Yes")],
                [InlineKeyboardButton("Ні, повторити заповнення форми", callback_data="No")],
            ]
            report_message = (
                              f"*Username:* {context.user_data.get('username')}\n"
                              f"*ПІБ:* {context.user_data.get('full_name')}\n"
                              f"*Звертатись:* {context.user_data.get('just_name')}\n"
                              f"*Факультет/інститут:* {context.user_data.get('faculty')}\n"
                              f"*Шифр групи:* {context.user_data.get('group')}\n"
                              f"*Можливість відвідувати КПІ:* {context.user_data.get('regularity')}\n"
                              f"*Обрані департаменти/служби:* {context.user_data.get('choice1')}{context.user_data.get('choice2')}\n"
                              f"*Дата народження:* {context.user_data.get('birthdate')}\n"
                              f"*Досвід:* {context.user_data.get('experience')}\n"
                              f"*Мотивація:* {context.user_data.get('motivation')}\n")
            context.user_data['report'] = report_message
            await query.message.reply_text(
                f"Дякуємо! Введені Вами дані:\n{report_message}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await context.bot.set_my_commands(ordinary_commands,scope=telegram.BotCommandScopeChat(update.message.chat_id))
            keyboard = [[InlineKeyboardButton("🔘 Ні, скасувати заповнення форми❌ 🔘 ", callback_data="none")]]
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            await query.message.reply_text("Заповнення форми успішно скасовано!\nЯк зміните своє рішення, то завжди можете повторити цю процедуру.")
            return ConversationHandler.END
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    none_keyboard=""
    if(query.data=="Yes"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Все вірно, надіслати 🔘 ", callback_data="none")],
        ]
    elif(query.data=="No"):
        none_keyboard = [
            [InlineKeyboardButton("🔘 Ні, повторити заповнення форми 🔘 ", callback_data="none")],
        ]
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(none_keyboard))
    while (query.data == "none"):
        query = update.callback_query
        await query.answer()
    if (query.data == "Yes"):
        keyboard = [
            [InlineKeyboardButton("Прийняти ✅ ", callback_data="good"), InlineKeyboardButton("Відхилити ❌ ", callback_data="bad")]
        ]
        form = await context.bot.send_message(chat_id=dev_chat_id,text=f"Нова заповнена форма!!!")
        await context.bot.edit_message_text(chat_id=dev_chat_id,message_id=form.message_id,text=f"📋Нова заповнена форма:\n*ID форми*: #T{query.message.chat.id}{((form.message_id) + 1)}\n{context.user_data.get('report')}",parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(keyboard))
        forms[int(form.message_id)]=(int(query.message.chat.id), int(query.message.message_id), 0)
        context.user_data.clear()
        await context.bot.set_my_commands(ordinary_commands, scope=telegram.BotCommandScopeChat(query.message.chat.id))
        return ConversationHandler.END
    elif (query.data == "No"):
        context.user_data.clear()
        await query.message.reply_text("1. ПІБ(повністю без скорочень):")
        return FULL_NAME


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # обробник кнопок під повідомленнями
    query = update.callback_query  # отримання черги повідомлень із кнопками
    await query.answer()
    if (query.message.message_id in forms.keys()):
        data = forms.get(int(query.message.message_id), ['None', 'None', 'None'])
        chat_id = int(data[0])
        reply_message_id = int(data[1])
        forms.pop(int(query.message.message_id))
        forms[int(query.message.message_id)] = (chat_id, reply_message_id, 1)
        if query.data == 'good':
            keyboard = [
                [InlineKeyboardButton("🔘 Прийнято ✅ 🔘", callback_data="none")]]
            text = "Заповнену вами форму прийнято! ☑️"
        elif query.data == 'bad':
            keyboard = [
                [InlineKeyboardButton("🔘 Відхилено ❌ 🔘", callback_data="none")]]
            text = "Заповнену вами форму відхилено! 🚫"
        else:
            return
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup, parse_mode="Markdown")  # модифікація повідомлення з формою
        await context.bot.send_message(text=text, chat_id=chat_id, reply_to_message_id=reply_message_id)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введення форми скасовано!")
    await context.bot.set_my_commands(ordinary_commands,scope=telegram.BotCommandScopeChat(update.message.chat_id))
    return ConversationHandler.END


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) != dev_chat_id:
        await update.message.reply_text("Невідома команда.")


async def post_init(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.set_my_commands(ordinary_commands)
    await context.bot.set_my_commands(
        [("start", "Запускає бота"), ("help", "Коротка довідка"), ("chat_id", "Показує ID цього чату")],
        scope=telegram.BotCommandScopeChat(dev_chat_id) )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a+") as file:
        file.write(f"{str(context.error)}\n{current_time}\n")



def main():
    reboot = True
    while reboot:
        try:
            app = ApplicationBuilder().token(telegram_token).post_init(post_init).read_timeout(
                read_timeout=60).connect_timeout(connect_timeout=60).build()
            conv_handler = ConversationHandler(
                entry_points=[(CommandHandler("join", join))],
                states={
                    USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
                    FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
                    JUST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, just_name)],
                    FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, faculty)],
                    GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, group)],
                    REGULARITY: [CallbackQueryHandler(regularity)],
                    DEPARTMENTS: [CallbackQueryHandler(departments_choice)],
                    BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_date)],
                    EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
                    MOTIVATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, motivation)],
                    ACCEPT: [CallbackQueryHandler(acceptance)],
                    CONFIRM: [CallbackQueryHandler(confirm)],
                },
                fallbacks=[CommandHandler("cancel", cancel)],
            )
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help))
            app.add_handler(CommandHandler("chat_id", chat_id))
            app.add_handler(conv_handler)
            app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
            app.add_handler(CallbackQueryHandler(buttons))  # додавання обробника кнопок
            app.add_error_handler(error_handler)
            app.run_polling()
        except NetworkError as e:
            with open("log.txt", "a+") as file:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"{str(e)}\n{current_time}\n")
            time.sleep(30)

if __name__ == "__main__":
    main()