import telebot
from telebot import types
from flask import Flask, request
import os
import openai

TOKEN = os.environ.get("BOT_TOKEN")
AGENTROUTER_KEY = os.environ.get("AGENTROUTER_KEY")
USDT_WALLET = "0x4390c186a0B2b08b9423240D0719D2696a190a22"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💬 Chat AI', '🎨 Image', '🎬 Video')
    markup.add('💳 Buy $10 Lite', '💳 Buy $25 Pro')
    bot.send_message(message.chat.id, "🚀 Welcome to NebulaAI 🚀\n\nLite $10/mo + Pro $25/mo\n3 Free trial messages hain", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '💬 Chat AI')
def chat_ai(message):
    bot.send_message(message.chat.id, "Ok jani pucho kya puchna hai? 🤖")

@bot.message_handler(func=lambda m: m.text == '🎨 Image')
def img(message):
    bot.send_message(message.chat.id, "Prompt bhejo image ke liye")

@bot.message_handler(func=lambda m: m.text == '🎬 Video')
def vid(message):
    bot.send_message(message.chat.id, "Prompt bhejo video ke liye")

@bot.message_handler(func=lambda m: m.text == '💳 Buy $10 Lite')
def buy10(message):
    bot.send_message(message.chat.id, f"USDT bhej do: {USDT_WALLET}\n\nAmount: $10")

@bot.message_handler(func=lambda m: m.text == '💳 Buy $25 Pro')
def buy25(message):
    bot.send_message(message.chat.id, f"USDT bhej do: {USDT_WALLET}\n\nAmount: $25")

@bot.message_handler(content_types=['text'])
def ai_reply(message):
    if message.text in ['💬 Chat AI','🎨 Image','🎬 Video','💳 Buy $10 Lite','💳 Buy $25 Pro']:
        return
    try:
        client = openai.OpenAI(api_key=AGENTROUTER_KEY, base_url="https://agentrouter.org/")
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":message.text}])
        bot.send_message(message.chat.id, res.choices[0].message.content)
    except Exception as e:
        bot.send_message(message.chat.id, f"AgentRouter Error:\n{e}")
        print(f"FULL ERROR: {e}")

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get("WEBHOOK_URL") + "/" + TOKEN)
    return "Webhook set!", 200
