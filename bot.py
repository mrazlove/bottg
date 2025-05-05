import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.environ.get("7758579141:AAHpP65JwImvdAhUSQCYCphPbQcj5y3tq60")

if not TOKEN:
    raise Exception("Ошибка: переменная BOT_TOKEN не задана!")

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

CURRENCIES = "usd,eur,gbp,jpy,cny,try,pln,uah,kzt,cad,aud,chf,inr,brl,czk,hkd,krw,sek,sgd"

def get_rates():
    try:
        currencies = "usd,eur,gbp,jpy,cny,try,pln,uah,kzt,cad,aud,chf,inr,brl,czk,hkd,krw,sek,sgd"
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currencies},rub"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            raise Exception(f"CoinGecko вернул код {response.status_code}")

        data = response.json().get("bitcoin")
        if not data or "rub" not in data:
            raise Exception("Нет данных о рубле или bitcoin")

        btc_rub = data["rub"]
        message = ["Курс валют к рублю (RUB):"]
        for cur, val in data.items():
            if cur == "rub":
                continue
            rub_val = btc_rub / val
            message.append(f"1 {cur.upper()} = {round(rub_val, 2)} RUB")

        return "\n".join(message)

    except Exception as e:
        return f"Ошибка при получении данных: {e}"
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    webhook_url = os.environ.get("WEBHOOK_URL")  # https://your-service.onrender.com
    if webhook_url:
        bot.set_webhook(f"{webhook_url}/{TOKEN}")
        return f"Webhook установлен: {webhook_url}/{TOKEN}"
    return "Поставь переменную окружения WEBHOOK_URL"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
