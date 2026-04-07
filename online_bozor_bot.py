import telebot
from telebot import types
import os

TOKEN = "ВАШ_ТОКЕН"
OPERATOR_ID = 7740882890

bot = telebot.TeleBot(TOKEN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

user_cart = {}
user_data = {}
user_lang = {}

# 🌍 язык
TEXTS = {
    "ru": {
        "catalog": "Каталог 🛒",
        "cart": "Корзина 🧾",
        "choose": "Выберите категорию:",
        "drinks": "Напитки 🥤",
        "products": "Продукты 🛒",
        "empty": "🛒 Корзина пуста",
        "checkout": "Оформить заказ ✅",
        "phone": "📞 Введите номер:",
        "address": "📍 Введите адрес:",
        "done": "✅ Заказ отправлен!",
        "back": "⬅ Назад"
    },
    "uz": {
        "catalog": "Katalog 🛒",
        "cart": "Savat 🧾",
        "choose": "Kategoriya tanlang:",
        "drinks": "Ichimliklar 🥤",
        "products": "Mahsulotlar 🛒",
        "empty": "🛒 Savat bo‘sh",
        "checkout": "Buyurtma berish ✅",
        "phone": "📞 Telefon kiriting:",
        "address": "📍 Manzil kiriting:",
        "done": "✅ Buyurtma yuborildi!",
        "back": "⬅ Orqaga"
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

# 🥤 товары
drinks = {
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
    "Sprite": {
        "0.5 L": "sprite_05l.jpg",
        "1 L": "sprite_1l.jpg",
        "1.5 L": "sprite_15l.jpg"
    },
    "Flash Energy": "flash_250ml.jpg"
}

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
    markup.row(t["catalog"], t["cart"])

    bot.send_message(message.chat.id, "ONLINE BOZOR 🛒", reply_markup=markup)

# 📋 меню
@bot.message_handler(content_types=['text'])
def menu(message):
    lang = user_lang.get(message.chat.id, "ru")
    t = TEXTS[lang]

    if message.text == t["catalog"]:
        catalog(message)

    elif message.text == t["cart"]:
        show_cart(message.chat.id)

# 📂 каталог
def catalog(message):
    lang = user_lang.get(message.chat.id, "ru")
    t = TEXTS[lang]

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t["drinks"], callback_data="drinks"))
    markup.add(types.InlineKeyboardButton(t["products"], callback_data="products"))

    bot.send_message(message.chat.id, t["choose"], reply_markup=markup)

# 🥤 напитки
def show_drinks(chat_id):
    for name, data in drinks.items():
        markup = types.InlineKeyboardMarkup()

        if isinstance(data, dict):
            text = f"🥤 {name}\n"
            for size in data:
                text += f"\n{size} — {PRICES[size]} сум"
                markup.add(types.InlineKeyboardButton(f"➕ {size}", callback_data=f"add|{name}|{size}"))

            photo = list(data.values())[0]

        else:
            text = f"⚡ {name}\n💰 {PRICES['energy']} сум"
            markup.add(types.InlineKeyboardButton("➕ Добавить", callback_data=f"add|{name}"))
            photo = data

        try:
            with open(os.path.join(BASE_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

# 🛢 продукты
def show_products(chat_id):
    for name, (photo, key) in products.items():
        text = f"{name}\n💰 {PRICES[key]} сум"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Добавить", callback_data=f"add_product|{name}"))

        try:
            with open(os.path.join(BASE_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

# 🧾 корзина (с количеством!)
def show_cart(chat_id):
    cart = user_cart.get(chat_id, {})

    if not cart:
        bot.send_message(chat_id, "🛒 Пусто")
        return

    text = "🧾 Ваш заказ:\n\n"
    markup = types.InlineKeyboardMarkup()
    total = 0

    for item, data in cart.items():
        count = data["count"]
        price = data["price"]
        total += count * price

        text += f"{item} x{count} = {count*price} сум\n"

        markup.add(
            types.InlineKeyboardButton("➖", callback_data=f"minus|{item}"),
            types.InlineKeyboardButton("➕", callback_data=f"plus|{item}")
        )

    text += f"\n💰 Итого: {total}"

    markup.add(types.InlineKeyboardButton("✅ Оформить", callback_data="checkout"))

    bot.send_message(chat_id, text, reply_markup=markup)

# 🔘 кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "drinks":
        show_drinks(chat_id)

    elif call.data == "products":
        show_products(chat_id)

    elif call.data.startswith("add"):
        parts = call.data.split("|")
        name = parts[1]

        if len(parts) == 3:
            size = parts[2]
            price = PRICES[size]
            name += f" {size}"
        else:
            price = PRICES["energy"]

        cart = user_cart.setdefault(chat_id, {})

        if name in cart:
            cart[name]["count"] += 1
        else:
            cart[name] = {"count": 1, "price": price}

        bot.answer_callback_query(call.id, "Добавлено")

    elif call.data.startswith("add_product"):
        name = call.data.split("|")[1]
        key = products[name][1]
        price = PRICES[key]

        cart = user_cart.setdefault(chat_id, {})

        if name in cart:
            cart[name]["count"] += 1
        else:
            cart[name] = {"count": 1, "price": price}

        bot.answer_callback_query(call.id, "Добавлено")

    elif call.data.startswith("plus"):
        item = call.data.split("|")[1]
        user_cart[chat_id][item]["count"] += 1
        show_cart(chat_id)

    elif call.data.startswith("minus"):
        item = call.data.split("|")[1]
        user_cart[chat_id][item]["count"] -= 1

        if user_cart[chat_id][item]["count"] <= 0:
            del user_cart[chat_id][item]

        show_cart(chat_id)

    elif call.data == "checkout":
        bot.send_message(chat_id, "📞 Введите номер:")
        bot.register_next_step_handler(call.message, get_phone)

# 📞 телефон
def get_phone(message):
    user_data[message.chat.id] = {"phone": message.text}
    bot.send_message(message.chat.id, "📍 Введите адрес:")
    bot.register_next_step_handler(message, get_address)

# 📍 адрес
def get_address(message):
    cart = user_cart.get(message.chat.id, {})
    total = 0

    text = f"🛒 Новый заказ\n\nID: {message.chat.id}\n"
    text += f"📞 {user_data[message.chat.id]['phone']}\n"
    text += f"📍 {message.text}\n\n"

    for item, data in cart.items():
        total += data["count"] * data["price"]
        text += f"{item} x{data['count']} = {data['count']*data['price']} сум\n"

    text += f"\n💰 {total}"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Связаться", url=f"tg://user?id={message.chat.id}"))

    bot.send_message(OPERATOR_ID, text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Заказ отправлен!")

    user_cart[message.chat.id] = {}

# 🚀 запуск
bot.infinity_polling()
