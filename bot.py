import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения
TOKEN = os.environ.get("7758579141:AAHpP65JwImvdAhUSQCYCphPbQcj5y3tq60")
logging.info(f"[ОТЛАДКА] Переменная BOT_TOKEN = {TOKEN!r}")

if not TOKEN:
    raise Exception("Ошибка: переменная BOT_TOKEN не задана!")

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Получение курса валют
def get_rates():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,eur,gbp,rub"
    data = requests.get(url).json().get("bitcoin")
    if not data or "rub" not in data:
        return "Ошибка: не удалось получить данные от CoinGecko."
    btc_rub = data["rub"]
    message = ["Курс валют к рублю (RUB):"]
    for cur, val in data.items():
        if cur == "rub":
            continue
        rub_val = btc_rub / val
        message.append(f"1 {cur.upper()} = {round(rub_val, 2)} RUB")
    return "\n".join(message)

# Обработчик команд
def handle(update: Update, context):
    update.message.reply_text(get_rates())

dispatcher.add_handler(CommandHandler("start", handle))
dispatcher.add_handler(CommandHandler("rates", handle))

# Webhook обработчик
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Установка webhook
@app.route("/")
def index():
    url = os.environ.get("WEBHOOK_URL")
    logging.info(f"[ОТЛАДКА] WEBHOOK_URL = {url!r}")
    if url:
        bot.set_webhook(f"{url}/{TOKEN}")
        return f"Webhook установлен: {url}/{TOKEN}"
    return "Переменная WEBHOOK_URL не задана"

# Запуск Flask
if name == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
