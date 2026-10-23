import logging
import os
import re
import html
from urllib.parse import quote_plus
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)

# Вставь сюда НОВЫЙ токен, который выдаст @BotFather после перевыпуска старого.
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROUP_ID = -1004360454890
ADMIN_USERNAME = "shuxich"

LANGUAGE, START_ORDER, PHONE, ROLE, PICKUP, DESTINATION, BOOKING_TYPE, PASSENGERS, SEATING, PRICE, DATETIME, WISHES, PARCEL_TYPE, PARCEL_WEIGHT, PARCEL_SIZE, PARCEL_PHOTO = range(16)

LANGS = {
    "🇷🇺 Русский": "ru",
    "🇺🇿 O‘zbekcha": "uz",
    "🇬🇧 English": "en",
}

T = {
    "ru": {
        "welcome": "🚕 SAMARQAND ↔ TOSHKENT TAXI\n\n👋 Добро пожаловать!\nЗаказывайте поездки из Самарканда в Ташкент и обратно.\n⚡ Оформление займёт всего пару минут.\n🤝 С нами удобно, быстро и надёжно!\n\n🌐 Выберите язык:",
        "start_order": "📱 Начать оформление заказа",
        "phone": "📱 Сначала отправьте свой номер телефона кнопкой ниже.",
        "share_phone": "📱 Отправить мой номер телефона",
        "role": "Кто оформляет заказ?",
        "driver": "🚗 Водитель",
        "passenger": "🧍 Пассажир",
        "parcel": "📦 Передать посылку",
        "parcel_type_prompt": "📦 Что нужно передать? Выберите тип посылки:",
        "parcel_documents": "📄 Документы",
        "parcel_box": "📦 Коробка",
        "parcel_other": "🧳 Другое",
        "parcel_weight_prompt": "⚖️ Укажите вес посылки (например, 2 кг). Если неизвестен, напишите «не знаю».",
        "parcel_size_prompt": "📏 Укажите размеры (например, 30×20×10 см).",
        "parcel_photo_prompt": "📷 Прикрепить фото посылки? Отправьте фото или нажмите «Пропустить».",
        "parcel_photo_skip": "⏭ Пропустить",
        "role_error": "Выберите «Водитель» или «Пассажир».",
        "driver_info": "🚗 Хотите сотрудничать с нами?\n\nДля работы с нашей службой такси свяжитесь с администратором. Нажмите кнопку ниже, чтобы открыть его профиль.",
        "admin": "👤 Связаться с администратором",
        "pickup": "📍 Откуда забрать? Отправьте локацию кнопкой ниже или напишите адрес текстом.",
        "share_location": "📍 Отправить мою локацию",
        "cancel": "❌ Отмена",
        "pickup_ok": "✅ Место посадки получено.\n\nТеперь укажите место назначения: отправьте локацию или нажмите кнопку ввода адреса текстом.",
        "destination_text": "✍️ Ввести адрес текстом",
        "destination_prompt": "Напишите адрес назначения: город, район, улицу и дом, если известны.",
        "destination_error": "Укажите адрес подробнее или отправьте локацию кнопкой ниже.",
        "destination_ok": "✅ Место назначения получено. Выберите тип заказа.",
        "seats": "👥 По местам",
        "salon": "🚖 Весь салон",
        "booking_error": "Выберите «По местам» или «Весь салон».",
        "salon_price": "Укажите общую цену за весь салон, например 500 000 сум.",
        "passengers": "Сколько пассажиров/мест?",
        "passengers_error": "Выберите количество от 1 до 8.",
        "seating_prompt": "Как разместить пассажиров в салоне?",
        "seat_front": "💺 Переднее место",
        "seat_back": "💺 Заднее место",
        "seat_back_salon": "🚘 Один пассажир в заднем салоне",
        "seat_two_back": "💺 Два места сзади",
        "seat_salon": "🚘 Задний салон",
        "seat_front_back": "💺 Одно переднее и одно заднее место",
        "seat_three_back": "💺 Три места сзади",
        "seat_front_two_back": "💺 Одно спереди и два сзади",
        "seat_agreement": "🚕 Размещение по договорённости",
        "two_cars": "🚗🚗 Заказать две машины",
        "price": "Укажите цену за одного пассажира/место, например 200 000 сум.",
        "price_error": "Введите цену цифрами, например 200 000 сум.",
        "datetime": "🕒 На когда нужна поездка/передача? Напишите дату и время, например: завтра 07:00 или 20.10 07:00.",
        "datetime_error": "Укажите дату и время выезда.",
        "wishes": "Есть пожелания или дополнительная информация? Напишите их или нажмите «Без пожеланий».",
        "no_wishes": "Без пожеланий",
        "sent": "✅ Заказ оформлен и отправлен в группу!",
        "send_error": "❌ Не удалось отправить заказ в группу. Попробуйте позже или свяжитесь с администратором.",
        "cancelled": "Оформление отменено. Нажмите /start, чтобы начать заново.",
        "contact_error": "Пожалуйста, отправьте именно свой номер кнопкой Telegram.",
        "language_error": "Выберите язык кнопкой ниже.",
    },
    "uz": {
        "welcome": "🚕 SAMARQAND ↔ TOSHKENT TAXI\n\n👋 Xush kelibsiz!\nSamarqanddan Toshkentga va Toshkentdan Samarqandga safar buyurtma qiling.\n⚡ Buyurtma bir necha daqiqa oladi.\n🤝 Biz bilan qulay, tez va ishonchli!\n\n🌐 Tilni tanlang:",
        "start_order": "📱 Buyurtmani boshlash",
        "phone": "📱 Avval telefon raqamingizni quyidagi tugma orqali yuboring.",
        "share_phone": "📱 Telefon raqamimni yuborish",
        "role": "Buyurtmani kim bermoqda?",
        "driver": "🚗 Haydovchi",
        "passenger": "🧍 Yo‘lovchi",
        "parcel": "📦 Jo‘natma yuborish",
        "parcel_type_prompt": "📦 Nima yubormoqchisiz? Jo‘natma turini tanlang:",
        "parcel_documents": "📄 Hujjatlar",
        "parcel_box": "📦 Quti",
        "parcel_other": "🧳 Boshqa",
        "parcel_weight_prompt": "⚖️ Jo‘natma vaznini yozing (masalan, 2 kg). Bilmasangiz, «bilmayman» deb yozing.",
        "parcel_size_prompt": "📏 O‘lchamlarini yozing (masalan, 30×20×10 sm).",
        "parcel_photo_prompt": "📷 Jo‘natma rasmini qo‘shasizmi? Rasm yuboring yoki «O‘tkazib yuborish»ni bosing.",
        "parcel_photo_skip": "⏭ O‘tkazib yuborish",
        "role_error": "«Haydovchi» yoki «Yo‘lovchi»ni tanlang.",
        "driver_info": "🚗 Biz bilan hamkorlik qilmoqchimisiz?\n\nTaksi xizmatimiz bilan ishlash uchun administrator bilan bog‘laning. Quyidagi tugma orqali uning profilini oching.",
        "admin": "👤 Administrator bilan bog‘lanish",
        "pickup": "📍 Qayerdan olib ketaylik? Lokatsiya yuboring yoki manzilni matn bilan yozing.",
        "share_location": "📍 Joylashuvimni yuborish",
        "cancel": "❌ Bekor qilish",
        "pickup_ok": "✅ Olib ketish joyi qabul qilindi.\n\nEndi boradigan manzilni kiriting: lokatsiya yuboring yoki manzilni matn bilan kiritish tugmasini bosing.",
        "destination_text": "✍️ Manzilni matn bilan kiritish",
        "destination_prompt": "Boradigan manzilni yozing: shahar, tuman, ko‘cha va uy raqami.",
        "destination_error": "Manzilni batafsilroq yozing yoki lokatsiya yuboring.",
        "destination_ok": "✅ Manzil qabul qilindi. Buyurtma turini tanlang.",
        "seats": "👥 Joylar bo‘yicha",
        "salon": "🚖 Butun salon",
        "booking_error": "«Joylar bo‘yicha» yoki «Butun salon»ni tanlang.",
        "salon_price": "Butun salon uchun umumiy narxni kiriting, masalan 500 000 so‘m.",
        "passengers": "Nechta yo‘lovchi/joy?",
        "passengers_error": "1 dan 8 gacha bo‘lgan sonni tanlang.",
        "seating_prompt": "Yo‘lovchilar salonda qanday joylashadi?",
        "seat_front": "💺 Oldingi o‘rindiq",
        "seat_back": "💺 Orqa o‘rindiq",
        "seat_back_salon": "🚘 Bitta yo‘lovchi orqa salonda",
        "seat_two_back": "💺 Orqada ikkita o‘rindiq",
        "seat_salon": "🚘 Orqa salon",
        "seat_front_back": "💺 Bitta oldinda va bitta orqada",
        "seat_three_back": "💺 Orqada uchta o‘rindiq",
        "seat_front_two_back": "💺 Bitta oldinda va ikkitasi orqada",
        "seat_agreement": "🚕 Joylashuv kelishuv asosida",
        "two_cars": "🚗🚗 Ikkita mashina buyurtma qilish",
        "price": "Bir yo‘lovchi/joy narxini kiriting, masalan 200 000 so‘m.",
        "price_error": "Narxni raqam bilan kiriting, masalan 200 000 so‘m.",
        "datetime": "🕒 Safar/jo‘natma qachon kerak? Masalan: ertaga 07:00 yoki 20.10 07:00.",
        "datetime_error": "Jo‘nash sana va vaqtini kiriting.",
        "wishes": "Qo‘shimcha izoh bormi? Yozing yoki «Izoh yo‘q» tugmasini bosing.",
        "no_wishes": "Izoh yo‘q",
        "sent": "✅ Buyurtma rasmiylashtirildi va guruhga yuborildi!",
        "send_error": "❌ Buyurtmani guruhga yuborib bo‘lmadi. Keyinroq urinib ko‘ring yoki administrator bilan bog‘laning.",
        "cancelled": "Buyurtma bekor qilindi. Qayta boshlash uchun /start bosing.",
        "contact_error": "Iltimos, Telegram tugmasi orqali o‘z raqamingizni yuboring.",
        "language_error": "Quyidagi tugma orqali tilni tanlang.",
    },
    "en": {
        "welcome": "🚕 SAMARQAND ↔ TOSHKENT TAXI\n\n👋 Welcome!\nBook trips from Samarkand to Tashkent and back.\n⚡ Booking takes just a few minutes.\n🤝 Convenient, fast and reliable!\n\n🌐 Choose your language:",
        "start_order": "📱 Start booking",
        "phone": "📱 First, share your phone number using the button below.",
        "share_phone": "📱 Share my phone number",
        "role": "Who is making the booking?",
        "driver": "🚗 Driver",
        "passenger": "🧍 Passenger",
        "parcel": "📦 Send a parcel",
        "parcel_type_prompt": "📦 What would you like to send? Choose the parcel type:",
        "parcel_documents": "📄 Documents",
        "parcel_box": "📦 Box",
        "parcel_other": "🧳 Other",
        "parcel_weight_prompt": "⚖️ Enter the parcel weight (e.g. 2 kg). If unknown, type ‘unknown’.",
        "parcel_size_prompt": "📏 Enter dimensions (e.g. 30×20×10 cm).",
        "parcel_photo_prompt": "📷 Add a photo of the parcel? Send a photo or tap “Skip”.",
        "parcel_photo_skip": "⏭ Skip",
        "role_error": "Please choose Driver or Passenger.",
        "driver_info": "🚗 Want to work with us?\n\nContact our administrator to cooperate with our taxi service. Tap the button below to open the profile.",
        "admin": "👤 Contact administrator",
        "pickup": "📍 Where should we pick up? Share a location or type the address.",
        "share_location": "📍 Share my location",
        "cancel": "❌ Cancel",
        "pickup_ok": "✅ Pickup location received.\n\nNow enter the destination: share its location or tap the text-address button.",
        "destination_text": "✍️ Enter destination as text",
        "destination_prompt": "Enter the destination: city, district, street and house number if known.",
        "destination_error": "Please provide a more detailed destination or share its location.",
        "destination_ok": "✅ Destination received. Choose a booking type.",
        "seats": "👥 Per seat",
        "salon": "🚖 Entire car",
        "booking_error": "Choose Per seat or Entire car.",
        "salon_price": "Enter the total price for the entire car, e.g. 500,000 UZS.",
        "passengers": "How many passengers/seats?",
        "passengers_error": "Choose a number from 1 to 8.",
        "seating_prompt": "How should the passengers be seated?",
        "seat_front": "💺 Front seat",
        "seat_back": "💺 Rear seat",
        "seat_back_salon": "🚘 One passenger in the rear cabin",
        "seat_two_back": "💺 Two rear seats",
        "seat_salon": "🚘 Rear cabin",
        "seat_front_back": "💺 One front seat and one rear seat",
        "seat_three_back": "💺 Three rear seats",
        "seat_front_two_back": "💺 One front and two rear seats",
        "seat_agreement": "🚕 Seating by arrangement",
        "two_cars": "🚗🚗 Order two cars",
        "price": "Enter the price per passenger/seat, e.g. 200,000 UZS.",
        "price_error": "Enter the price using digits, e.g. 200,000 UZS.",
        "datetime": "🕒 When is the trip/delivery needed? Enter date and time, e.g. tomorrow 07:00 or 20.10 07:00.",
        "datetime_error": "Please enter the departure date and time.",
        "wishes": "Any wishes or extra information? Type them or tap No extra notes.",
        "no_wishes": "No extra notes",
        "sent": "✅ Your booking has been sent to the group!",
        "send_error": "❌ Could not send the booking to the group. Please try later or contact the administrator.",
        "cancelled": "Booking cancelled. Send /start to begin again.",
        "contact_error": "Please share your own phone number using Telegram's button.",
        "language_error": "Please choose a language using the buttons below.",
    },
}

def tr(context, key):
    lang = context.user_data.get("lang", "ru")
    return T.get(lang, T["ru"]).get(key, T["ru"].get(key, key))

def lang_keyboard():
    return ReplyKeyboardMarkup([list(LANGS.keys())], resize_keyboard=True, one_time_keyboard=True)

def start_keyboard(context):
    return ReplyKeyboardMarkup([[tr(context, "start_order")]], resize_keyboard=True, one_time_keyboard=True)

def contact_keyboard(context):
    return ReplyKeyboardMarkup([[KeyboardButton(tr(context, "share_phone"), request_contact=True)]],
                               resize_keyboard=True, one_time_keyboard=True)

def location_keyboard(context):
    return ReplyKeyboardMarkup([[KeyboardButton(tr(context, "share_location"), request_location=True)],
                                [tr(context, "cancel")]], resize_keyboard=True, one_time_keyboard=True)

def destination_keyboard(context):
    return ReplyKeyboardMarkup([[tr(context, "destination_text")], [tr(context, "cancel")]],
                               resize_keyboard=True, one_time_keyboard=True)

def booking_keyboard(context):
    return ReplyKeyboardMarkup([[tr(context, "seats"), tr(context, "salon")], [tr(context, "cancel")]],
                               resize_keyboard=True, one_time_keyboard=True)

def passengers_keyboard(context):
    return ReplyKeyboardMarkup([["1", "2", "3", "4"], ["5", "6", "7", "8"], [tr(context, "cancel")]],
                               resize_keyboard=True, one_time_keyboard=True)

def seating_keyboard(context, count):
    keys = {
        1: ["seat_front", "seat_back", "seat_back_salon"],
        2: ["seat_two_back", "seat_salon", "seat_front_back"],
        3: ["seat_three_back", "seat_front_two_back"],
        4: ["seat_agreement"],
    }
    options = [tr(context, key) for key in keys.get(count, ["two_cars"])]
    rows = [[option] for option in options]
    rows.append([tr(context, "cancel")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)

def cancel_keyboard(context):
    return ReplyKeyboardMarkup([[tr(context, "cancel")]], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    if update.message:
        await update.message.reply_text(
            "🚕 SAMARQAND ↔ TOSHKENT TAXI\n\n"
            "🇷🇺 Добро пожаловать! Поездки Самарканд ↔ Ташкент в обе стороны.\n"
            "🇺🇿 Xush kelibsiz! Samarqand ↔ Toshkent yo‘nalishida ikki tomonga safarlar.\n"
            "🇬🇧 Welcome! Trips between Samarkand and Tashkent, both ways.\n\n"
            "🌐 Выберите язык / Tilni tanlang / Choose your language:",
            reply_markup=lang_keyboard()
        )
    return LANGUAGE

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text not in LANGS:
        await update.message.reply_text(tr(context, "language_error"), reply_markup=lang_keyboard())
        return LANGUAGE
    context.user_data["lang"] = LANGS[text]
    await update.message.reply_text(tr(context, "welcome"), reply_markup=start_keyboard(context))
    return START_ORDER

async def begin_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text != tr(context, "start_order"):
        await update.message.reply_text(tr(context, "start_order"), reply_markup=start_keyboard(context))
        return START_ORDER
    context.user_data["order"] = {}
    await update.message.reply_text(tr(context, "phone"), reply_markup=contact_keyboard(context))
    return PHONE

async def receive_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    contact = msg.contact if msg else None
    user = update.effective_user
    if not contact:
        await msg.reply_text(tr(context, "contact_error"), reply_markup=contact_keyboard(context))
        return PHONE
    if user and contact.user_id and contact.user_id != user.id:
        await msg.reply_text(tr(context, "contact_error"), reply_markup=contact_keyboard(context))
        return PHONE
    context.user_data.setdefault("order", {})["phone"] = contact.phone_number
    await msg.reply_text(tr(context, "role"),
                         reply_markup=ReplyKeyboardMarkup([[tr(context, "driver"), tr(context, "passenger")], [tr(context, "parcel")], [tr(context, "cancel")]],
                                                          resize_keyboard=True, one_time_keyboard=True))
    return ROLE

async def receive_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    choice = (msg.text or "").strip()
    if choice == tr(context, "cancel"):
        return await cancel(update, context)
    if choice not in (tr(context, "driver"), tr(context, "passenger"), tr(context, "parcel")):
        await msg.reply_text(tr(context, "role_error"),
                             reply_markup=ReplyKeyboardMarkup([[tr(context, "driver"), tr(context, "passenger")]],
                                                              resize_keyboard=True, one_time_keyboard=True))
        return ROLE
    if choice == tr(context, "driver"):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(tr(context, "admin"), url=f"https://t.me/{ADMIN_USERNAME}")]])
        await msg.reply_text(tr(context, "driver_info"), reply_markup=kb)
        context.user_data.pop("order", None)
        return ConversationHandler.END
    if choice == tr(context, "parcel"):
        context.user_data["order"]["role"] = "Передача посылки"
        await msg.reply_text(tr(context, "pickup"), reply_markup=location_keyboard(context))
        return PICKUP
    context.user_data["order"]["role"] = "Пассажир"
    await msg.reply_text(tr(context, "pickup"), reply_markup=location_keyboard(context))
    return PICKUP

async def receive_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    order = context.user_data["order"]
    if msg.location:
        loc = msg.location
        order["pickup_lat"], order["pickup_lon"] = loc.latitude, loc.longitude
        order["pickup_url"] = f"https://www.google.com/maps/search/?api=1&query={loc.latitude},{loc.longitude}"
        order["pickup_display"] = f"{loc.latitude:.6f}, {loc.longitude:.6f}"
    elif len(text) >= 3 and text != tr(context, "share_location"):
        order["pickup_display"] = text
        order["pickup_url"] = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(text + ", Uzbekistan")
    else:
        await msg.reply_text(tr(context, "pickup"), reply_markup=location_keyboard(context))
        return PICKUP
    await msg.reply_text(tr(context, "pickup_ok"), reply_markup=destination_keyboard(context))
    return DESTINATION

async def receive_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    order = context.user_data["order"]
    if msg.location:
        loc = msg.location
        order["destination"] = f"{loc.latitude:.6f}, {loc.longitude:.6f}"
        order["destination_url"] = f"https://www.google.com/maps/search/?api=1&query={loc.latitude},{loc.longitude}"
        order["destination_lat"], order["destination_lon"] = loc.latitude, loc.longitude
    elif text == tr(context, "destination_text"):
        await msg.reply_text(tr(context, "destination_prompt"), reply_markup=cancel_keyboard(context))
        return DESTINATION
    elif len(text) >= 3:
        order["destination"] = text
        order.pop("destination_lat", None)
        order.pop("destination_lon", None)
        order.pop("destination_url", None)
    else:
        await msg.reply_text(tr(context, "destination_error"), reply_markup=destination_keyboard(context))
        return DESTINATION
    if order.get("role") == "Передача посылки":
        await msg.reply_text(tr(context, "parcel_type_prompt"),
            reply_markup=ReplyKeyboardMarkup([[tr(context, "parcel_documents"), tr(context, "parcel_box")],
                                              [tr(context, "parcel_other")], [tr(context, "cancel")]],
                                             resize_keyboard=True, one_time_keyboard=True))
        return PARCEL_TYPE
    await msg.reply_text(tr(context, "destination_ok"), reply_markup=booking_keyboard(context))
    return BOOKING_TYPE

async def receive_parcel_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    choice = (msg.text or "").strip()
    if choice == tr(context, "cancel"):
        return await cancel(update, context)
    options = {tr(context, "parcel_documents"): "Документы", tr(context, "parcel_box"): "Коробка", tr(context, "parcel_other"): "Другое"}
    if choice not in options:
        await msg.reply_text(tr(context, "parcel_type_prompt"),
            reply_markup=ReplyKeyboardMarkup([[tr(context, "parcel_documents"), tr(context, "parcel_box")], [tr(context, "parcel_other")], [tr(context, "cancel")]], resize_keyboard=True, one_time_keyboard=True))
        return PARCEL_TYPE
    context.user_data["order"]["parcel_type"] = options[choice]
    await msg.reply_text(tr(context, "parcel_weight_prompt"), reply_markup=cancel_keyboard(context))
    return PARCEL_WEIGHT

async def receive_parcel_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    if not text or len(text) > 100:
        await msg.reply_text(tr(context, "parcel_weight_prompt"), reply_markup=cancel_keyboard(context))
        return PARCEL_WEIGHT
    context.user_data["order"]["parcel_weight"] = text
    await msg.reply_text(tr(context, "parcel_size_prompt"), reply_markup=cancel_keyboard(context))
    return PARCEL_SIZE

async def receive_parcel_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    if not text or len(text) > 150:
        await msg.reply_text(tr(context, "parcel_size_prompt"), reply_markup=cancel_keyboard(context))
        return PARCEL_SIZE
    context.user_data["order"]["parcel_size"] = text
    await msg.reply_text(
        tr(context, "parcel_photo_prompt"),
        reply_markup=ReplyKeyboardMarkup([[tr(context, "parcel_photo_skip")], [tr(context, "cancel")]],
                                         resize_keyboard=True, one_time_keyboard=True)
    )
    return PARCEL_PHOTO

async def receive_parcel_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.text == tr(context, "cancel"):
        return await cancel(update, context)
    if msg.photo:
        context.user_data["order"]["parcel_photo_file_id"] = msg.photo[-1].file_id
        await msg.reply_text(tr(context, "price"), reply_markup=cancel_keyboard(context))
        return PRICE
    if (msg.text or "").strip() == tr(context, "parcel_photo_skip"):
        context.user_data["order"]["parcel_photo_file_id"] = None
        await msg.reply_text(tr(context, "price"), reply_markup=cancel_keyboard(context))
        return PRICE
    await msg.reply_text(
        tr(context, "parcel_photo_prompt"),
        reply_markup=ReplyKeyboardMarkup([[tr(context, "parcel_photo_skip")], [tr(context, "cancel")]],
                                         resize_keyboard=True, one_time_keyboard=True)
    )
    return PARCEL_PHOTO

async def receive_booking_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    choice = (msg.text or "").strip()
    if choice == tr(context, "cancel"):
        return await cancel(update, context)
    if choice not in (tr(context, "seats"), tr(context, "salon")):
        await msg.reply_text(tr(context, "booking_error"), reply_markup=booking_keyboard(context))
        return BOOKING_TYPE
    order = context.user_data["order"]
    order["booking_type"] = "Салон" if choice == tr(context, "salon") else "По местам"
    if order["booking_type"] == "Салон":
        order["passengers"] = "Весь салон"
        await msg.reply_text(tr(context, "salon_price"), reply_markup=cancel_keyboard(context))
        return PRICE
    await msg.reply_text(tr(context, "passengers"), reply_markup=passengers_keyboard(context))
    return PASSENGERS

async def receive_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    if not re.fullmatch(r"\d{1,2}", text) or not 1 <= int(text) <= 8:
        await msg.reply_text(tr(context, "passengers_error"), reply_markup=passengers_keyboard(context))
        return PASSENGERS
    count = int(text)
    order = context.user_data["order"]
    order["passengers"] = text
    if count >= 5:
        order["cars_needed"] = "2"
        order["seating"] = "two_cars"
        await msg.reply_text(tr(context, "price"), reply_markup=cancel_keyboard(context))
        return PRICE
    order["cars_needed"] = "1"
    await msg.reply_text(
        tr(context, "seating_prompt"),
        reply_markup=seating_keyboard(context, count)
    )
    return SEATING

async def receive_seating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    count = int(context.user_data["order"].get("passengers", "1"))
    valid = [tr(context, key) for key in {
        1: ["seat_front", "seat_back", "seat_back_salon"],
        2: ["seat_two_back", "seat_salon", "seat_front_back"],
        3: ["seat_three_back", "seat_front_two_back"],
        4: ["seat_agreement"],
    }.get(count, [])]
    if text not in valid:
        await msg.reply_text(
            tr(context, "seating_prompt"),
            reply_markup=seating_keyboard(context, count)
        )
        return SEATING
    option_keys = {
        1: ["seat_front", "seat_back", "seat_back_salon"],
        2: ["seat_two_back", "seat_salon", "seat_front_back"],
        3: ["seat_three_back", "seat_front_two_back"],
        4: ["seat_agreement"],
    }
    chosen_key = next((key for key in option_keys[count] if text == tr(context, key)), None)
    context.user_data["order"]["seating"] = chosen_key
    await msg.reply_text(tr(context, "price"), reply_markup=cancel_keyboard(context))
    return PRICE

async def receive_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    digits = re.sub(r"\D", "", text)
    if not digits or len(digits) > 10:
        await msg.reply_text(tr(context, "price_error"), reply_markup=cancel_keyboard(context))
        return PRICE
    amount = int(digits)
    formatted = f"{amount:,}".replace(",", " ") + " сум"
    order = context.user_data["order"]
    if order.get("role") == "Передача посылки":
        order["price_label"] = "Цена за передачу посылки"
    elif order.get("booking_type") == "Салон":
        order["price_label"] = "Цена за весь салон"
    else:
        order["price_label"] = "Цена за пассажира"
    order["price"] = formatted
    await msg.reply_text(tr(context, "datetime"), reply_markup=cancel_keyboard(context))
    return DATETIME

async def receive_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    if len(text) < 2:
        await msg.reply_text(tr(context, "datetime_error"), reply_markup=cancel_keyboard(context))
        return DATETIME
    context.user_data["order"]["datetime"] = text
    await msg.reply_text(tr(context, "wishes"),
                         reply_markup=ReplyKeyboardMarkup([[tr(context, "no_wishes")], [tr(context, "cancel")]],
                                                          resize_keyboard=True, one_time_keyboard=True))
    return WISHES

async def receive_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = (msg.text or "").strip()
    if text == tr(context, "cancel"):
        return await cancel(update, context)
    context.user_data["order"]["wishes"] = "Не указаны" if text == tr(context, "no_wishes") else text
    return await send_order(update, context)


GROUP_TEXT = {
    "ru": {
        "title": "🚕 <b>НОВЫЙ ЗАКАЗ</b>",
        "role": "🧾 <b>Тип заказа:</b>", "parcel_type": "📦 <b>Тип отправления:</b>", "parcel_weight": "⚖️ <b>Вес:</b>", "parcel_size": "📏 <b>Размер:</b>",
        "pickup": "📍 <b>Место посадки:</b>",
        "destination": "🏁 <b>Куда едет:</b>",
        "passengers": "👥 <b>Пассажиры:</b>",
        "seating": "💺 <b>Размещение:</b>",
        "cars": "🚗 <b>Количество машин:</b>",
        "phone": "📞 <b>Телефон:</b>",
        "price_seat": "💰 <b>Цена за пассажира:</b>",
        "price_car": "💰 <b>Цена за весь салон:</b>",
        "datetime": "🕒 <b>Дата и время:</b>",
        "wishes": "📝 <b>Пожелания:</b>",
        "client": "👤 <b>Профиль клиента:</b>",
        "pickup_link": "Открыть место посадки",
        "destination_link": "Открыть место назначения",
        "owner": "Владелец группы",
        "owner_link": "Связаться с Шухратом",
        "route_button": "🗺️ Открыть маршрут на карте",
        "pickup_button": "📍 Открыть место посадки",
        "destination_button": "🏁 Открыть место назначения",
    },
    "uz": {
        "title": "🚕 <b>YANGI BUYURTMA</b>",
        "role": "🧾 <b>Buyurtma turi:</b>", "parcel_type": "📦 <b>Jo‘natma turi:</b>", "parcel_weight": "⚖️ <b>Vazni:</b>", "parcel_size": "📏 <b>O‘lchami:</b>",
        "pickup": "📍 <b>Olib ketish joyi:</b>",
        "destination": "🏁 <b>Qayerga boradi:</b>",
        "passengers": "👥 <b>Yo‘lovchilar:</b>",
        "seating": "💺 <b>Joylashuv:</b>",
        "cars": "🚗 <b>Mashinalar soni:</b>",
        "phone": "📞 <b>Telefon:</b>",
        "price_seat": "💰 <b>Bir yo‘lovchi uchun narx:</b>",
        "price_car": "💰 <b>Butun salon narxi:</b>",
        "datetime": "🕒 <b>Sana va vaqt:</b>",
        "wishes": "📝 <b>Qo‘shimcha izoh:</b>",
        "client": "👤 <b>Mijoz profili:</b>",
        "pickup_link": "Olib ketish joyini ochish",
        "destination_link": "Boradigan manzilni ochish",
        "owner": "Guruh egasi",
        "owner_link": "Shuxrat bilan bog‘lanish",
        "route_button": "🗺️ Xaritada marshrutni ochish",
        "pickup_button": "📍 Olib ketish joyini ochish",
        "destination_button": "🏁 Boradigan manzilni ochish",
    },
    "en": {
        "title": "🚕 <b>NEW BOOKING</b>",
        "role": "🧾 <b>Order type:</b>", "parcel_type": "📦 <b>Parcel type:</b>", "parcel_weight": "⚖️ <b>Weight:</b>", "parcel_size": "📏 <b>Dimensions:</b>",
        "pickup": "📍 <b>Pickup location:</b>",
        "destination": "🏁 <b>Destination:</b>",
        "passengers": "👥 <b>Passengers:</b>",
        "seating": "💺 <b>Seating:</b>",
        "cars": "🚗 <b>Number of cars:</b>",
        "phone": "📞 <b>Phone:</b>",
        "price_seat": "💰 <b>Price per passenger:</b>",
        "price_car": "💰 <b>Price for the entire car:</b>",
        "datetime": "🕒 <b>Date and time:</b>",
        "wishes": "📝 <b>Notes:</b>",
        "client": "👤 <b>Client profile:</b>",
        "pickup_link": "Open pickup location",
        "destination_link": "Open destination",
        "owner": "Group owner",
        "owner_link": "Contact Shukhrat",
        "route_button": "🗺️ Open route in Maps",
        "pickup_button": "📍 Open pickup location",
        "destination_button": "🏁 Open destination",
    },
}

def build_group_order(order, client_link, lang):
    # Group post is bilingual/trilingual, but parcel orders show parcel-specific fields only.
    sections = []
    phone = html.escape(order.get("phone", "Не указано"))
    price = html.escape(order.get("price", "Не указано"))
    date_time = html.escape(order.get("datetime", "Не указано"))
    wishes = html.escape(order.get("wishes", "Не указаны"))
    pickup_url = order.get("pickup_url")
    pickup_display = html.escape(order.get("pickup_display", "Не указано"))
    destination_link = order.get("destination_url")
    if destination_link:
        destination_text = '<a href="' + html.escape(destination_link, quote=True) + '">{}</a>'
    else:
        destination_text = html.escape(order.get("destination", "Не указано"))

    is_parcel = order.get("role") == "Передача посылки"
    for code in ("ru", "uz", "en"):
        labels = GROUP_TEXT[code]
        dest = destination_text.format(labels["destination_link"]) if destination_link else destination_text
        pickup = (f'<a href="{html.escape(pickup_url, quote=True)}">{labels["pickup_link"]}</a>'
                  if pickup_url else pickup_display)

        if is_parcel:
            # One compact trilingual parcel post instead of repeating the full request 3 times.
            if code != "ru":
                continue
            section = (
                "📦 <b>ПОСЫЛКА | JO‘NATMA | PARCEL</b>\n\n"
                f"📍 Забрать | Olib ketish | From: {pickup}\n"
                f"🏁 Доставить | Yetkazish | To: {dest}\n"
                f"📦 Тип | Turi | Type: {html.escape(order.get('parcel_type', '—'))}\n"
                f"⚖️ Вес | Vazn | Weight: {html.escape(order.get('parcel_weight', '—'))}\n"
                f"📏 Размер | O‘lcham | Size: {html.escape(order.get('parcel_size', '—'))}\n"
                f"💰 Цена | Narx | Price: {price}\n"
                f"🕒 Время | Vaqt | Time: {date_time}\n"
                f"📞 Телефон | Telefon | Phone: {phone}\n"
                + (f"📝 Примечание | Izoh | Notes: {wishes}\n" if order.get("wishes") and order.get("wishes") not in ("Не указаны", "Не указано") else "")
                + (f'👤 <b>Профиль:</b> {client_link}\n' if client_link else '')
                + f'\n<b>Владелец | Guruh egasi | Owner:</b> <a href="https://t.me/{ADMIN_USERNAME}">@{ADMIN_USERNAME}</a>'
            )
        else:
            # Compact trilingual passenger booking in one message.
            if code != "ru":
                continue
            passengers = html.escape(order.get("passengers", "—"))
            seating_key = order.get("seating", "")
            seating = html.escape(T["ru"].get(seating_key, seating_key or "—"))
            price_key = "price_car" if order.get("booking_type") == "Салон" else "price_seat"
            price_label = "Цена | Narx | Price"
            section = (
                "🚕 <b>ЗАКАЗ ТАКСИ | TAKSI BUYURTMASI | TAXI BOOKING</b>\n\n"
                f"📍 Откуда | Qayerdan | From: {pickup}\n"
                f"🏁 Куда | Qayerga | To: {dest}\n"
                f"👥 Пассажиры | Yo‘lovchilar | Passengers: {passengers}\n"
                + (f"💺 Место | O‘rindiq | Seat: {seating}\n" if seating_key else "")
                + (f"🚗 Машины | Mashinalar | Cars: {html.escape(order.get('cars_needed', '1'))}\n" if int(order.get("passengers", "1")) >= 5 else "")
                + f"💰 {price_label}: {price}\n"
                + (f"👤 За человека | Bir kishi uchun | Per person: {price}\n" if order.get("booking_type") != "Салон" and int(order.get("passengers", "1")) < 5 else "")
                + f"🕒 Время | Vaqt | Time: {date_time}\n"
                f"📞 Телефон | Telefon | Phone: {phone}\n"
                + (f"📝 Пожелания | Istaklar | Notes: {wishes}\n" if order.get("wishes") and order.get("wishes") not in ("Не указаны", "Не указано") else "")
                + (f'👤 <b>Профиль клиента | Mijoz profili | Client:</b> {client_link}\n' if client_link else '')
                + f'\n<b>Владелец | Guruh egasi | Owner:</b> <a href="https://t.me/{ADMIN_USERNAME}">@{ADMIN_USERNAME}</a>'
            )
        sections.append(section)
    return "\n\n━━━━━━━━━━━━━━━━━━━━\n\n".join(sections)

async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    order = context.user_data.get("order", {})
    user = update.effective_user
    # Show client contact only when the customer has a public Telegram username.
    # Without a username, omit both the profile line and the contact button.
    if user and user.username:
        client_url = f"https://t.me/{user.username}"
        client_link = f'<a href="{html.escape(client_url, quote=True)}">Открыть профиль клиента</a>'
    else:
        client_url = None
        client_link = None

    if "destination_lat" in order:
        dest_for_map = f'{order["destination_lat"]},{order["destination_lon"]}'
    else:
        dest_for_map = quote_plus(order["destination"] + ", Uzbekistan")
    if "pickup_lat" in order:
        pickup_for_map = f'{order["pickup_lat"]},{order["pickup_lon"]}'
    else:
        pickup_for_map = quote_plus(order.get("pickup_display", "Uzbekistan") + ", Uzbekistan")
    map_url = (
        "https://www.google.com/maps/dir/?api=1"
        f'&origin={pickup_for_map}'
        f"&destination={dest_for_map}&travelmode=driving"
    )
    destination_link = order.get("destination_url")
    destination_text = (f'<a href="{html.escape(destination_link, quote=True)}">Открыть место назначения</a>'
                        if destination_link else html.escape(order["destination"]))
    phone = html.escape(order.get("phone", "Не указано"))
    price = html.escape(order.get("price", "Не указано"))
    date_time = html.escape(order.get("datetime", "Не указано"))
    wishes = html.escape(order.get("wishes", "Не указаны"))
    pickup_url = html.escape(order.get("pickup_url", ""), quote=True)
    pickup_display = html.escape(order.get("pickup_display", "Не указано"))
    text_group = build_group_order(order, client_link, context.user_data.get("lang", "ru"))
    button_labels = GROUP_TEXT.get(context.user_data.get("lang", "ru"), GROUP_TEXT["ru"])
    rows = [
        [InlineKeyboardButton(button_labels["route_button"], url=map_url)],
        [InlineKeyboardButton(button_labels["pickup_button"], url=order["pickup_url"])],
    ]
    if destination_link:
        rows.append([InlineKeyboardButton(button_labels["destination_button"], url=destination_link)])
    if client_url:
        rows.append([InlineKeyboardButton(
            "👤 Связаться с клиентом" if context.user_data.get("lang", "ru") == "ru"
            else ("👤 Mijoz bilan bog‘lanish" if context.user_data.get("lang") == "uz"
                  else "👤 Contact customer"),
            url=client_url
        )])
    try:
        parcel_photo_id = order.get("parcel_photo_file_id") if order.get("role") == "Передача посылки" else None
        if parcel_photo_id:
            # Send the compact trilingual order as the photo caption so it appears
            # directly underneath the parcel photo in one Telegram message.
            await context.bot.send_photo(
                chat_id=GROUP_ID, photo=parcel_photo_id, caption=text_group,
                parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(rows)
            )
        else:
            await context.bot.send_message(
                chat_id=GROUP_ID, text=text_group, parse_mode=ParseMode.HTML,
                disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(rows)
            )
        await msg.reply_text(tr(context, "sent"), reply_markup=ReplyKeyboardRemove())
    except Exception:
        logging.exception("Failed to send order to group")
        await msg.reply_text(tr(context, "send_error"), reply_markup=ReplyKeyboardRemove())
    context.user_data.pop("order", None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("order", None)
    if update.message:
        await update.message.reply_text(tr(context, "cancelled"), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in the hosting environment before starting the bot.")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app = Application.builder().token(TOKEN).build()
    flow = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            START_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, begin_order)],
            PHONE: [
                MessageHandler(filters.CONTACT, receive_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, begin_order),
            ],
            ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_role)],
            PICKUP: [MessageHandler((filters.LOCATION | filters.TEXT) & ~filters.COMMAND, receive_pickup)],
            PARCEL_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_parcel_type)],
            PARCEL_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_parcel_weight)],
            PARCEL_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_parcel_size)],
            PARCEL_PHOTO: [MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, receive_parcel_photo)],
            DESTINATION: [MessageHandler((filters.LOCATION | filters.TEXT) & ~filters.COMMAND, receive_destination)],
            BOOKING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_booking_type)],
            PASSENGERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_passengers)],
            SEATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_seating)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price)],
            DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_datetime)],
            WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wishes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(flow)
    print("Бот запущен. Для остановки нажми Ctrl+C.")
    app.run_polling()

if __name__ == "__main__":
    main()
