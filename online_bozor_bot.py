import telebot
from telebot import types
import os

TOKEN = "ВАШ_ТОКЕН"
OPERATOR_ID = 7740882890

bot = telebot.TeleBot(TOKEN)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "ONLINE BOZOR")

user_cart = {}

# 💰 цены
PRICES = {
    "0.5 L": 10000,
    "1 L": 14000,
    "1.5 L": 15000,
    "energy": 12000,
    "oil": 8000,
    "flour": 25000
}

# 📦 структура магазина
catalog_data = {
    "🥤 Напитки": {
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
            }
        },
        "⚡ Энергетики": {
            "Flash Energy": "flash_250ml.jpg"
        }
    },
    "🛒 Продукты": {
        "🛢️ Масло": {
            "Масло": ("oil.jpg", "oil")
        },
        "🌾 Мука": {
            "Мука": ("flour.jpg", "flour")
        }
    }
}

# ▶️ старт
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 Каталог", "🧾 Корзина")
    bot.send_message(message.chat.id, "ONLINE BOZOR 🛒", reply_markup=markup)

# 📋 меню
@bot.message_handler(content_types=['text'])
def menu(message):
    if message.text == "🛒 Каталог":
        show_main_categories(message.chat.id)

    elif message.text == "🧾 Корзина":
        show_cart(message.chat.id)

# 📂 главные категории
def show_main_categories(chat_id):
    markup = types.InlineKeyboardMarkup()

    for cat in catalog_data:
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"main|{cat}"))

    bot.send_message(chat_id, "Выберите категорию:", reply_markup=markup)

# 📂 подкатегории
def show_subcategories(chat_id, main_cat):
    markup = types.InlineKeyboardMarkup()

    for sub in catalog_data[main_cat]:
        markup.add(types.InlineKeyboardButton(sub, callback_data=f"sub|{main_cat}|{sub}"))

    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_main"))

    bot.send_message(chat_id, "Выберите:", reply_markup=markup)

# 📦 товары
def show_products(chat_id, main_cat, sub_cat):
    items = catalog_data[main_cat][sub_cat]

    for name, data in items.items():
        markup = types.InlineKeyboardMarkup()

        # напитки с размерами
        if isinstance(data, dict):
            text = f"{name}\n"
            for size in data:
                text += f"\n{size} — {PRICES[size]} сум"
                markup.add(types.InlineKeyboardButton(f"➕ {size}", callback_data=f"add|{name}|{size}"))
            photo = list(data.values())[0]

        # обычные товары
        else:
            photo, key = data
            price = PRICES[key]
            text = f"{name}\n💰 {price} сум"
            markup.add(types.InlineKeyboardButton("➕ Добавить", callback_data=f"add_product|{name}"))

        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data=f"back_sub|{main_cat}"))

        try:
            with open(os.path.join(IMG_DIR, photo), "rb") as img:
                bot.send_photo(chat_id, img, caption=text, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)

# 🧾 корзина
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

        text += f"{item} x{count} = {count*price}\n"

        markup.add(
            types.InlineKeyboardButton("➖", callback_data=f"minus|{item}"),
            types.InlineKeyboardButton("➕", callback_data=f"plus|{item}")
        )

    text += f"\n💰 Итого: {total}"
    bot.send_message(chat_id, text, reply_markup=markup)

# 🔘 кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass

    data = call.data.split("|")

    if data[0] == "main":
        show_subcategories(chat_id, data[1])

    elif data[0] == "sub":
        show_products(chat_id, data[1], data[2])

    elif call.data == "back_main":
        show_main_categories(chat_id)

    elif data[0] == "back_sub":
        show_subcategories(chat_id, data[1])

    elif data[0] == "add":
        name = data[1]
        size = data[2]
        price = PRICES[size]
        name += f" {size}"

        cart = user_cart.setdefault(chat_id, {})
        cart[name] = cart.get(name, {"count": 0, "price": price})
        cart[name]["count"] += 1

        show_cart(chat_id)

    elif data[0] == "add_product":
        name = data[1]

        key = "oil" if "Масло" in name else "flour"
        price = PRICES[key]

        cart = user_cart.setdefault(chat_id, {})
        cart[name] = cart.get(name, {"count": 0, "price": price})
        cart[name]["count"] += 1

        show_cart(chat_id)

    elif data[0] == "plus":
        item = data[1]
        if item in user_cart.get(chat_id, {}):
            user_cart[chat_id][item]["count"] += 1
        show_cart(chat_id)

    elif data[0] == "minus":
        item = data[1]
        if item in user_cart.get(chat_id, {}):
            user_cart[chat_id][item]["count"] -= 1
            if user_cart[chat_id][item]["count"] <= 0:
                del user_cart[chat_id][item]
        show_cart(chat_id)

# 🚀 запуск
bot.infinity_polling()
