import telebot
from telebot import types
import os

TOKEN = "TELEGRAM_BOT_TOKEN"
OPERATOR_ID = 7740882890

bot = telebot.TeleBot(TOKEN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

user_cart = {}
user_data = {}

# 💰 цены
PRICES = {
    "0.5 L": 10000,
    "1 L": 14000,
    "1.5 L": 15000,
    "energy": 12000,
    "oil": 20000,
    "flour": 15000
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
    markup.row("Каталог 🛒", "Мои заказы 📦")
    bot.send_message(message.chat.id, "👋 Добро пожаловать в ONLINE BOZOR!", reply_markup=markup)

# 📋 меню
@bot.message_handler(content_types=['text'])
def main_menu(message):
    if message.text == "Каталог 🛒":
        catalog_menu(message)
    elif message.text == "Мои заказы 📦":
        show_cart(message)

# 📂 каталог
def catalog_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Напитки 🥤", callback_data="drinks"))
    markup.add(types.InlineKeyboardButton("Продукты 🛒", callback_data="products"))
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)

# 🥤 напитки (С ЦЕНАМИ!)
def show_drinks(chat_id):
    for drink, data in drinks.items():
        markup = types.InlineKeyboardMarkup()

        if isinstance(data, dict):
            text = f"{drink}\n"
            for size in data:
                price = PRICES[size]
                text += f"\n{size} — {price} сум"
                markup.add(types.InlineKeyboardButton(f"{size} ➕", callback_data=f"add|{drink}|{size}"))

            photo = list(data.values())[0]

        else:
            price = PRICES["energy"]
            text = f"{drink}\n\n💰 {price} сум"
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
        price = PRICES[key]

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить ➕", callback_data=f"add_product|{name}"))

        text = f"{name}\n\n💰 {price} сум"

        try:
            with open(os.path.join(BASE_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

# 🛒 корзина
def show_cart(message):
    cart = user_cart.get(message.chat.id, [])

    if not cart:
        bot.send_message(message.chat.id, "🛒 Корзина пуста")
        return

    total = 0
    text = "🛒 Ваш заказ:\n\n"

    for item, price in cart:
        text += f"• {item} — {price} сум\n"
        total += price

    text += f"\n💰 Итого: {total} сум"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Оформить заказ ✅", callback_data="checkout"))

    bot.send_message(message.chat.id, text, reply_markup=markup)

# 🔘 кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "drinks":
        show_drinks(call.message.chat.id)

    elif call.data == "products":
        show_products(call.message.chat.id)

    elif call.data.startswith("add|"):
        parts = call.data.split("|")
        item = parts[1]

        if len(parts) == 3:
            size = parts[2]
            price = PRICES[size]
            item += f" {size}"
        else:
            price = PRICES["energy"]

        user_cart.setdefault(call.message.chat.id, []).append((item, price))
        bot.answer_callback_query(call.id, f"{item} добавлен ✅")

    elif call.data.startswith("add_product"):
        name = call.data.split("|")[1]
        key = products[name][1]
        price = PRICES[key]

        user_cart.setdefault(call.message.chat.id, []).append((name, price))
        bot.answer_callback_query(call.id, f"{name} добавлен ✅")

    elif call.data == "checkout":
        bot.send_message(call.message.chat.id, "📞 Введите номер:")
        bot.register_next_step_handler(call.message, get_phone)

# 📞 телефон
def get_phone(message):
    user_data[message.chat.id] = {"phone": message.text}
    bot.send_message(message.chat.id, "📍 Введите адрес:")
    bot.register_next_step_handler(message, get_address)

# 📍 адрес
def get_address(message):
    user_data[message.chat.id]["address"] = message.text

    cart = user_cart.get(message.chat.id, [])
    total = sum(price for _, price in cart)

    text = "🛒 НОВЫЙ ЗАКАЗ\n\n"
    text += f"👤 ID: {message.chat.id}\n"
    text += f"📞 {user_data[message.chat.id]['phone']}\n"
    text += f"📍 {user_data[message.chat.id]['address']}\n\n"

    for item, price in cart:
        text += f"• {item} — {price} сум\n"

    text += f"\n💰 ИТОГО: {total} сум"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Написать клиенту", url=f"tg://user?id={message.chat.id}"))

    bot.send_message(OPERATOR_ID, text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Заказ отправлен!")

    user_cart[message.chat.id] = []

# 🚀 запуск
bot.polling(none_stop=True)