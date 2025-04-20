import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# === Настройки ===
TELEGRAM_TOKEN = '8048222463:AAFyo0C1Wi5kE58X6KvIiVOyISZIZ_He7Uo'
DEEPINFRA_API_KEY = 'RVT0XwsAltfXRINYNp4ISBWWMChYruv5'
MODEL = 'mistralai/Mixtral-8x7B-Instruct-v0.1'

# === Логика состояний ===
CHOOSE_MODE, ASK_QUESTION = range(2)

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['📚 Объясни тему', '🧮 Реши задачу']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я AI Репетитор по математике. Выбери режим:",
        reply_markup=markup
    )
    return CHOOSE_MODE

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['mode'] = text
    await update.message.reply_text("Хорошо, напиши свой вопрос или тему:")
    return ASK_QUESTION

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode', '')
    user_input = update.message.text

    prompt = f"""
Ты — дружелюбный AI-репетитор по математике. Объясни ученику понятным языком.
Режим: {mode}
Запрос: {user_input}
"""

    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://api.deepinfra.com/v1/chat/completions",
        headers=headers,
        json=json_data
    )

    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        await update.message.reply_text(content)
    else:
        await update.message.reply_text("Ошибка при обращении к AI :(")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог завершён. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END

# === Запуск ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print("Бот запущен!")
    app.run_polling()
