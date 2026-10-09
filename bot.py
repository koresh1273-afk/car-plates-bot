import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8428532637:AAHN8JAmEoGTyFxfNNZoCiQTDtgwYYL4pJg"

LETTERS = ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х']
REGIONS = ['777', '99', '199', '77', '178', '98', '123', '161', '799']

players = {}

def get_player(user_id):
    if user_id not in players:
        players[user_id] = {"balance": 1000, "inventory": []}
    return players[user_id]

def generate_plate():
    l1, l2, l3 = random.choices(LETTERS, k=3)
    d1, d2, d3 = [random.randint(0, 9) for _ in range(3)]
    region = random.choice(REGIONS)
    digits = f"{d1}{d2}{d3}"
    plate = f"{l1}{digits}{l2}{l3} | {region}"
    
    if d1 == d2 == d3 and l1 == l2 == l3:
        rarity, bonus = "🔥 ЛЕГЕНДАРНЫЙ (Три буквы и три цифры)", 5000
    elif d1 == d2 == d3:
        rarity, bonus = "💎 ОЧЕНЬ РЕДКИЙ (Три цифры)", 1500
    elif digits in ["001", "007", "777"]:
        rarity, bonus = "⭐ БЛАТНОЙ", 1000
    elif d1 == d3:
        rarity, bonus = "✨ ЗЕРКАЛКА", 300
    else:
        rarity, bonus = "Обычный", 50

    return plate, rarity, bonus

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_player(update.effective_user.id)
    keyboard = [
        ["🎲 Крутить номер (100 руб)"],
        ["💼 Мой гараж", "💰 Баланс"]
    ]
    await update.message.reply_text(
        "Добро пожаловать в «Выбивание автономеров»!\n"
        "Вам начислено 1000 рублей.\nЖмите кнопку ниже!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    player = get_player(update.effective_user.id)
    
    if text == "🎲 Крутить номер (100 руб)":
        if player["balance"] < 100:
            await update.message.reply_text("❌ Недостаточно средств!")
            return
            
        player["balance"] -= 100
        plate, rarity, bonus = generate_plate()
        player["balance"] += bonus
        player["inventory"].append(f"{plate} — {rarity}")
        
        await update.message.reply_text(
            f"🚘 **Вам выпал номер:**\n`{plate}`\n\n"
            f"Редкость: {rarity}\n"
            f"Приз: +{bonus} руб.\n"
            f"Баланс: {player['balance']} руб.",
            parse_mode="Markdown"
        )
    elif text == "💼 Мой гараж":
        if not player["inventory"]:
            await update.message.reply_text("Гараж пока пуст.")
        else:
            items = "\n".join([f"• {p}" for p in player["inventory"][-10:]])
            await update.message.reply_text(f"🚗 Последние выбитые номера:\n\n{items}")
    elif text == "💰 Баланс":
        await update.message.reply_text(f"💵 Ваш баланс: {player['balance']} руб.")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

def main():
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот успешно запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
