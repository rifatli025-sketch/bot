import telebot
from telebot import types
import os

TOKEN = "ВАШ_ТОКЕН"
OPERATOR_ID = 7740882890

bot = telebot.TeleBot(TOKEN)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "ONLINE BOZOR")

user_cart = {}
user_data = {}
user_lang = {}

# 🌍 тексты
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в ONLINE BOZOR!\n\n🛒 Удобные онлайн покупки\n📦 Быстрая доставка\n\nВыберите действие 👇",
        "catalog": "🛒 Каталог",
        "cart": "🧾 Корзина",
        "choose": "Выберите категорию:",
        "drinks": "🥤 Напитки",
        "products": "🛒 Продукты",
        "back": "⬅ Назад",
        "empty": "🛒 Корзина пуста",
        "checkout": "✅ Оформить заказ",
        "phone": "📞 Введите номер:",
        "address": "📍 Введите адрес:",
        "done": "✅ Заказ отправлен!"
    },
    "uz": {
        "welcome": "👋 ONLINE BOZOR ga xush kelibsiz!\n\n🛒 Qulay onlayn xarid\n📦 Tez yetkazib berish\n\nTanlang 👇",
        "catalog": "🛒 Katalog",
        "cart": "🧾 Savat",
        "choose": "Kategoriya tanlang:",
        "drinks": "🥤 Ichimliklar",
        "products": "🛒 Mahsulotlar",
        "back": "⬅ Orqaga",
        "empty": "🛒 Savat bo‘sh",
        "checkout": "✅ Buyurtma berish",
        "phone": "📞 Telefon kiriting:",
        "address": "📍 Manzil kiriting:",
        "done": "✅ Buyurtma yuborildi!"
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
drink_categories = {
    "🥤 Газировка": {
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
        }
    },
    "⚡ Энергетики": {
        "Flash Energy": "flash_250ml.jpg"
    }
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
    bot.send_message(message.chat.id, "🌍 Выберите язык / Tilni tanlang:", reply_markup=markup)

# 🌍 выбор языка
@bot.message_handler(func=lambda m: m.text in ["🇷🇺 Русский", "🇺🇿 O‘zbek"])
def set_lang(message):
    lang = "ru" if "Русский" in message.text else "uz"
    user_lang[message.chat.id] = lang
    t = TEXTS[lang]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(t["catalog"], t["cart"])

    bot.send_message(message.chat.id, t["welcome"], reply_markup=markup)

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

# 🥤 категории напитков
def show_drink_categories(chat_id):
    markup = types.InlineKeyboardMarkup()

    for category in drink_categories:
        markup.add(types.InlineKeyboardButton(category, callback_data=f"drink_cat|{category}"))

    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_catalog"))

    bot.send_message(chat_id, "Выберите напитки:", reply_markup=markup)

# 🥤 товары
def show_drinks(chat_id, category):
    drinks = drink_categories[category]

    for name, data in drinks.items():
        markup = types.InlineKeyboardMarkup()

        if isinstance(data, dict):
            text = f"{name}\n"
            for size in data:
                text += f"\n{size} — {PRICES[size]} сум"
                markup.add(types.InlineKeyboardButton(f"➕ {size}", callback_data=f"add|{name}|{size}"))

            photo = list(data.values())[0]
        else:
            text = f"{name}\n💰 {PRICES['energy']} сум"
            markup.add(types.InlineKeyboardButton("➕ Добавить", callback_data=f"add|{name}"))
            photo = data

        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="drinks"))

        try:
            with open(os.path.join(IMG_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

# 🛒 категории продуктов
def show_product_categories(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🛢️ Масло", callback_data="cat_oil"),
        types.InlineKeyboardButton("🌾 Мука", callback_data="cat_flour")
    )
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_catalog"))

    bot.send_message(chat_id, "Выберите продукт:", reply_markup=markup)

# 🧾 корзина
def show_cart(chat_id):
    lang = user_lang.get(chat_id, "ru")
    t = TEXTS[lang]

    cart = user_cart.get(chat_id, {})

    if not cart:
        bot.send_message(chat_id, t["empty"])
        return

    text = "🧾\n\n"
    markup = types.InlineKeyboardMarkup()
    total = 0

    for item, data in cart.items():
        count = data["count"]
        price = data["price"]
        total += count * price

        text += f"{item} x{count} = {count*price}\n"

        markup.add(
            types.InlineKeyboardButton("➖", callback_data=f"minus|{item}"),
            types.InlineKeyboardButton("➕", callback_data=f"plus|{item}")
        )

    text += f"\n💰 {total}"
    markup.add(types.InlineKeyboardButton(t["checkout"], callback_data="checkout"))

    bot.send_message(chat_id, text, reply_markup=markup)

# 🔘 кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass

    if call.data == "drinks":
        show_drink_categories(chat_id)

    elif call.data.startswith("drink_cat"):
        category = call.data.split("|")[1]
        show_drinks(chat_id, category)

    elif call.data == "products":
        show_product_categories(chat_id)

    elif call.data == "cat_oil":
        add_product(chat_id, "Масло 🛢️")

    elif call.data == "cat_flour":
        add_product(chat_id, "Мука 🌾")

    elif call.data == "back_catalog":
        catalog(call.message)

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
        cart[name] = cart.get(name, {"count": 0, "price": price})
        cart[name]["count"] += 1

        show_cart(chat_id)

    elif call.data.startswith("plus"):
        item = call.data.split("|")[1]
        if item in user_cart.get(chat_id, {}):
            user_cart[chat_id][item]["count"] += 1
        show_cart(chat_id)

    elif call.data.startswith("minus"):
        item = call.data.split("|")[1]
        if item in user_cart.get(chat_id, {}):
            user_cart[chat_id][item]["count"] -= 1
            if user_cart[chat_id][item]["count"] <= 0:
                del user_cart[chat_id][item]
        show_cart(chat_id)

    elif call.data == "checkout":
        bot.send_message(chat_id, TEXTS[user_lang[chat_id]]["phone"])
        bot.register_next_step_handler(call.message, get_phone)

# 🛒 добавление продукта
def add_product(chat_id, name):
    key = products[name][1]
    price = PRICES[key]

    cart = user_cart.setdefault(chat_id, {})
    cart[name] = cart.get(name, {"count": 0, "price": price})
    cart[name]["count"] += 1

    show_cart(chat_id)

# 📞 телефон
def get_phone(message):
    user_data[message.chat.id] = {"phone": message.text}
    bot.send_message(message.chat.id, TEXTS[user_lang[message.chat.id]]["address"])
    bot.register_next_step_handler(message, get_address)

# 📍 адрес
def get_address(message):
    cart = user_cart.get(message.chat.id, {})
    total = 0

    text = f"🛒 Заказ\n\n📞 {user_data[message.chat.id]['phone']}\n📍 {message.text}\n\n"

    for item, data in cart.items():
        total += data["count"] * data["price"]
        text += f"{item} x{data['count']} = {data['count']*data['price']}\n"

    text += f"\n💰 {total}"

    bot.send_message(OPERATOR_ID, text)
    bot.send_message(message.chat.id, TEXTS[user_lang[message.chat.id]]["done"])

    user_cart[message.chat.id] = {}

# 🚀 запуск
bot.infinity_polling()
