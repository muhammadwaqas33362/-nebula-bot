import telebot
from telebot import types
from flask import Flask, request
import os
import openai

TOKEN = os.environ.get("BOT_TOKEN")  # Railway me dalna hai
AGENTROUTER_KEY = os.environ.get("AGENTROUTER_KEY")  # Railway me dalna hai
USDT_WALLET = "0x4390c186a0B2b08b9423240D0719D2696a190a22"
PRICE_LITE = 10
PRICE_PRO = 25

bot = telebot.TeleBot(TOKEN)
openai.api_key = AGENTROUTER_KEY
openai.api_base = "https://agentrouter.org/"
paid_users = {}

app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💬 Chat AI', '🎨 Image', '🎬 Video')
    markup.add('💳 Buy $10 Lite', '💳 Buy $25 Pro')
    bot.send_message(message.chat.id, f"🚀 *Welcome to NebulaAI* 🚀\n\n*Lite $10/mo* + *Pro $25/mo*\n3 Free trial messages hain", reply_markup=markup, parse_mode="Markdown")

# Yahan baaki commands add kar dena

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get("WEBHOOK_URL") + "/" + TOKEN)
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))