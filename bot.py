from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Укажите ваш токен бота и ID группы с менеджерами
BOT_TOKEN = '7555522970:AAEW2d7EQzK4AN7lJvzT-qcaXCG-XEjlxSI'
MANAGER_GROUP_ID = -1002423545386 # ID группы с менеджерами

# Словарь для хранения активных заявок
active_requests = {}


# Команда /start
async def start(update: Update, context):
    user = update.message.from_user
    keyboard = [[
        InlineKeyboardButton("Відправити заявку", callback_data="send_request")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привіт, я бот для відправлення заяви для отримання допомоги з медичною додвікою.\n Завдяки мені ти зможеш отримати довідку необхідну для навчання в автошколі та складання іспитів в Сервісних Центрах України",
        reply_markup=reply_markup)


    # Обработка нажатия кнопки
async def button_click(update: Update, context):

    query = update.callback_query
    user = query.from_user

    # Создаем заявку и сохраняем в словарь
    active_requests[user.id] = {
        'user_id': user.id,
        'username': user.username or user.full_name,
        'chat_id': query.message.chat.id,
    }

    # Отправляем сообщение в группу с менеджерами
    manager_message = (
        f"Новая заявка от пользователя @{user.username if user.username else user.full_name}.\n"
        f""
        f"---SYSTEM---"
        f"ID: {user.id}"  # Добавляем ID пользователя
    )
    await context.bot.send_message(chat_id=MANAGER_GROUP_ID,
                                   text=manager_message)

    # Уведомляем пользователя об успешной отправке
    await query.answer("Завява надіслана, спецаліст скоро зв'яжеться з Вами.")
    await query.edit_message_text(
        "Ваша заява успішно відправлена! Очікуйте відповідь спецаліста.")


# Обработка сообщений от пользователей
async def user_message(update: Update, context):
    user = update.message.from_user
    if user.id in active_requests:
        # Отправляем сообщение от пользователя в группу менеджеров
        manager_message = f"Новое сообщение от @{user.username or user.full_name}:\n {update.message.text}\n\n\n---SYSTEM---\n ID: {user.id}"
        await context.bot.send_message(chat_id=MANAGER_GROUP_ID,
                                       text=manager_message)
    else:
        await update.message.reply_text(
            "Спочатку відкрийте нову заяву, /start.")


# Обработка сообщений от менеджеров
async def manager_message(update: Update, context):
                # Проверяем, что сообщение является ответом на сообщение в группе
                if update.message.reply_to_message:
                    # Пытаемся извлечь ID пользователя из текста сообщения
                    try:
                        user_id_line = update.message.reply_to_message.text.split("\n")[-1]  # Последняя строка
                        user_id = int(user_id_line.replace("ID: ", "").strip())

                        if user_id in active_requests:
                            chat_id = active_requests[user_id]['chat_id']
                            await context.bot.send_message(chat_id=chat_id, text=f"Відповідь від спеціаліста:\n {update.message.text}")
                    except (ValueError, AttributeError):
                        await update.message.reply_text("Не удалось найти ID пользователя в ответе.")


# Основной код для запуска бота
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler('start', start))

    # Обработчик нажатий на кнопки
    application.add_handler(
        CallbackQueryHandler(button_click, pattern="send_request"))

    # Обработчики сообщений
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.Chat(MANAGER_GROUP_ID),
                       user_message))
    application.add_handler(
        MessageHandler(filters.Chat(MANAGER_GROUP_ID), manager_message))

    # Запуск бота
    application.run_polling()
