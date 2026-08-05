@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    text = message.text

    if text == '💬 Chat AI':
        bot.send_message(user_id, "Ok jani pucho kya puchna hai? 🤖")
        return

    if text == '💳 Buy $10 Lite':
        bot.send_message(user_id, f"USDT bhej do: `{USDT_WALLET}`\n\nAmount: $10\nReceipt bhejte hi Lite on ho jayega", parse_mode="Markdown")
        return

    if text == '💳 Buy $25 Pro':
        bot.send_message(user_id, f"USDT bhej do: `{USDT_WALLET}`\n\nAmount: $25\nReceipt bhejte hi Pro on ho jayega", parse_mode="Markdown")
        return

    try:
        client = openai.OpenAI(
            api_key=AGENTROUTER_KEY,
            base_url="https://agentrouter.org/"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": text}]
        )
        reply = response.choices[0].message.content
        bot.send_message(user_id, reply)
    except Exception as e:
        bot.send_message(user_id, f"Error: {e}")
