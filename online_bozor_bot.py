import telebot
from telebot import types
import os

TOKEN = "ВАШ_ТОКЕН"
OPERATOR_ID = 418034107

bot = telebot.TeleBot(TOKEN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

user_cart = {}
user_data = {}
user_lang = {}

# 🌍 переводы (ТОЛЬКО RU + UZ)
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в ONLINE BOZOR!",
        "catalog": "Каталог 🛒",
        "orders": "Мои заказы 📦",
        "choose_category": "Выберите категорию:",
        "drinks": "Напитки 🥤",
        "products": "Продукты 🛒",
        "cart_empty": "🛒 Корзина пуста",
        "checkout": "Оформить заказ ✅",
        "enter_phone": "📞 Введите номер:",
        "enter_address": "📍 Введите адрес:",
        "order_done": "✅ Заказ отправлен!",
        "delete": "❌ Удалить"
    },
    "uz": {
        "welcome": "👋 ONLINE BOZOR ga xush kelibsiz!",
        "catalog": "Katalog 🛒",
        "orders": "Buyurtmalar 📦",
        "choose_category": "Kategoriya tanlang:",
        "drinks": "Ichimliklar 🥤",
        "products": "Mahsulotlar 🛒",
        "cart_empty": "🛒 Savat bo‘sh",
        "checkout": "Buyurtma berish ✅",
        "enter_phone": "📞 Telefon kiriting:",
        "enter_address": "📍 Manzil kiriting:",
        "order_done": "✅ Buyurtma yuborildi!",
        "delete": "❌ O‘chirish"
    }
}

# 💰 цены
PRICES = {
    "0.5 L": 10000,
    "1 L": 14000,
    "1.5 L": 15000,
    "energy": 12000,
    "oil": 8000,
    "flour": 25000
}

# 🥤 напитки
drinks = {
    "Енергетик Flash 250 ml": "flash_250ml.jpg",
    "Енергетик 18+ 250 ml": "18plus_250ml.jpg",
    "Сок Bliss Персик 1 L": "bliss_peach_1l.jpg",
    "Сочная Долина Сок Персик": "sochnaya_peach.jpg",

    "Sprite": {
        "0.5 L": "sprite_05l.jpg",
        "1 L": "sprite_1l.jpg",
        "1.5 L": "sprite_15l.jpg"
    },

    "Coca-Cola": {
        "0.5 L": "coca_05l.jpg",
        "1 L": "coca_1l.jpg",
        "1.5 L": "coca_15l.jpg"
    },

    "Fanta": {
        "0.5 L": "fanta_05l.jpg",
        "1 L": "fanta_1l.jpg",
        "1.5 L": "fanta_15l.jpg"
    },

    "Енергетик Горилла 0,5 L": "gorilla_05l.jpg",
    "Енергетик Adrinoline 250 ml": "adrinoline_250ml.jpg"
}

# 🛒 продукты
products = {
    "Масло 🛢️": ("oil.jpg", "oil"),
    "Мука 🌾": ("flour.jpg", "flour")
}

# ▶️ старт
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🇷🇺 Русский", "🇺🇿 O‘zbek")
    bot.send_message(message.chat.id, "🌍 Выберите язык:", reply_markup=markup)

# 🌍 язык
@bot.message_handler(func=lambda m: m.text in ["🇷🇺 Русский", "🇺🇿 O‘zbek"])
def set_lang(message):
    user_lang[message.chat.id] = "ru" if "Русский" in message.text else "uz"
    t = TEXTS[user_lang[message.chat.id]]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(t["catalog"], t["orders"])

    bot.send_message(message.chat.id, t["welcome"], reply_markup=markup)

# 📋 меню
@bot.message_handler(content_types=['text'])
def main_menu(message):
    lang = user_lang.get(message.chat.id, "ru")
    t = TEXTS[lang]

    if message.text == t["catalog"]:
        catalog_menu(message, t)
    elif message.text == t["orders"]:
        show_cart(message)

# 📂 каталог
def catalog_menu(message, t):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t["drinks"], callback_data="drinks"))
    markup.add(types.InlineKeyboardButton(t["products"], callback_data="products"))
    bot.send_message(message.chat.id, t["choose_category"], reply_markup=markup)

# 🛒 корзина с удалением
def show_cart(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "ru")
    t = TEXTS[lang]

    cart = user_cart.get(chat_id, [])

    if not cart:
        bot.send_message(chat_id, t["cart_empty"])
        return

    total = 0
    markup = types.InlineKeyboardMarkup()

    text = "🛒:\n\n"
    for i, (item, price) in enumerate(cart):
        text += f"{i+1}. {item} — {price} сум\n"
        total += price
        markup.add(types.InlineKeyboardButton(f"{t['delete']} {i+1}", callback_data=f"remove|{i}"))

    text += f"\n💰 {total} сум"
    markup.add(types.InlineKeyboardButton(t["checkout"], callback_data="checkout"))

    bot.send_message(chat_id, text, reply_markup=markup)

# 🔘 кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "drinks":
        show_drinks(chat_id)

    elif call.data == "products":
        show_products(chat_id)

    elif call.data.startswith("add|"):
        parts = call.data.split("|")
        item = parts[1]

        if len(parts) == 3:
            size = parts[2]
            price = PRICES[size]
            item += f" {size}"
        else:
            price = PRICES["energy"]

        user_cart.setdefault(chat_id, []).append((item, price))
        bot.answer_callback_query(call.id, "Добавлено ✅")

    elif call.data.startswith("add_product"):
        name = call.data.split("|")[1]
        key = products[name][1]
        price = PRICES[key]

        user_cart.setdefault(chat_id, []).append((name, price))
        bot.answer_callback_query(call.id, "Добавлено ✅")

    elif call.data.startswith("remove|"):
        index = int(call.data.split("|")[1])
        user_cart[chat_id].pop(index)
        bot.answer_callback_query(call.id, "Удалено ❌")
        show_cart(call.message)

    elif call.data == "checkout":
        bot.send_message(chat_id, TEXTS[user_lang.get(chat_id, "ru")]["enter_phone"])
        bot.register_next_step_handler(call.message, get_phone)

# 📞 телефон
def get_phone(message):
    user_data[message.chat.id] = {"phone": message.text}
    bot.send_message(message.chat.id, TEXTS[user_lang.get(message.chat.id, "ru")]["enter_address"])
    bot.register_next_step_handler(message, get_address)

# 📍 адрес
def get_address(message):
    user_data[message.chat.id]["address"] = message.text

    cart = user_cart.get(message.chat.id, [])
    total = sum(price for _, price in cart)

    text = f"🛒 Новый заказ\n\nID: {message.chat.id}\n"
    text += f"📞 {user_data[message.chat.id]['phone']}\n"
    text += f"📍 {user_data[message.chat.id]['address']}\n\n"

    for item, price in cart:
        text += f"• {item} — {price} сум\n"

    text += f"\n💰 {total} сум"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Связаться", url=f"tg://user?id={message.chat.id}"))

    bot.send_message(OPERATOR_ID, text, reply_markup=markup)
    bot.send_message(message.chat.id, TEXTS[user_lang.get(message.chat.id, "ru")]["order_done"])

    user_cart[message.chat.id] = []

# 🥤 напитки (оставь как у тебя)
def show_drinks(chat_id):
    for drink, data in drinks.items():
        markup = types.InlineKeyboardMarkup()

        if isinstance(data, dict):
            text = f"{drink}\n"
            for size in data:
                text += f"\n{size} — {PRICES[size]} сум"
                markup.add(types.InlineKeyboardButton(f"{size} ➕", callback_data=f"add|{drink}|{size}"))
            photo = list(data.values())[0]
        else:
            text = f"{drink}\n💰 {PRICES['energy']} сум"
            markup.add(types.InlineKeyboardButton("Добавить ➕", callback_data=f"add|{drink}"))
            photo = data

        try:
            with open(os.path.join(BASE_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

# 🛢️ продукты
def show_products(chat_id):
    for name, (photo, key) in products.items():
        text = f"{name}\n💰 {PRICES[key]} сум"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить ➕", callback_data=f"add_product|{name}"))

        try:
            with open(os.path.join(BASE_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# 🚀 запуск
bot.infinity_polling()
