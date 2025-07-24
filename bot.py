import re
from datetime import datetime

import telebot
from telebot import types

from config import BOT_TOKEN
from keyboards import (language_keyboard, slot_choice_keyboard, slots_keyboard, 
                      main_menu_keyboard, confirm_keyboard, service_type_keyboard,
                      driver_type_keyboard, livestream_keyboard, delivery_keyboard,
                      urgency_keyboard, payment_keyboard, location_keyboard)
from translations import TRANSLATIONS
from users import get_user_lang, set_user_lang, resolve_lang
from calendar_api import get_free_slots, find_nearest_slots, book_slot

bot = telebot.TeleBot(BOT_TOKEN)
pending_bookings = {}  # chat_id -> {'service_type': str, 'details': dict}

# Service type constants
SERVICE_HAIR = 'hair'
SERVICE_DRIVER = 'driver'
SERVICE_LIVESTREAM = 'livestream'
SERVICE_DELIVERY = 'delivery'

def get_phrase(chat_id, key, **kwargs):
    lang = get_user_lang(chat_id)
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    return text.format(**kwargs)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user
    chat_id = message.chat.id

    # set lang, if it hasn't set yet
    if not get_user_lang(chat_id):
        resolve_lang(chat_id, user.language_code)

    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    bot.send_message(chat_id, get_phrase(chat_id, "welcome", name=name))
    bot.send_message(chat_id, get_phrase(chat_id, "main_menu_prompt"), 
                     reply_markup=main_menu_keyboard(chat_id))

@bot.message_handler(commands=['language'])
def handle_language(message):
    chat_id = message.chat.id
    kb, options = language_keyboard()
    bot.send_message(chat_id, get_phrase(chat_id, "choose_language"), reply_markup=kb)

@bot.message_handler(func=lambda msg: msg.text in ["🇺🇸 English", "🇪🇸 Español", "🔥 ATL Slang"])
def handle_language_selection(message):
    chat_id = message.chat.id
    text = message.text

    lang_code = {
        "🇺🇸 English": "en",
        "🇪🇸 Español": "es",
        "🔥 ATL Slang": "atl"
    }.get(text, "en")

    set_user_lang(chat_id, lang_code)
    bot.send_message(chat_id, get_phrase(chat_id, "language_set"), 
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(chat_id, get_phrase(chat_id, "main_menu_prompt"), 
                     reply_markup=main_menu_keyboard(chat_id))

@bot.message_handler(func=lambda msg: msg.text in ["💈 Book Barber", "💈 Barbero", "💈 Fade Me Up"])
def handle_hair_booking(message):
    chat_id = message.chat.id
    pending_bookings[chat_id] = {'service_type': SERVICE_HAIR, 'details': {}}
    bot.send_message(chat_id, get_phrase(chat_id, "hair_service_prompt"),
                     reply_markup=service_type_keyboard(chat_id))

@bot.message_handler(func=lambda msg: msg.text in ["🚗 Get Driver", "🚗 Conductor", "🚗 Pull Up"])
def handle_driver_booking(message):
    chat_id = message.chat.id
    pending_bookings[chat_id] = {'service_type': SERVICE_DRIVER, 'details': {}}
    bot.send_message(chat_id, get_phrase(chat_id, "driver_service_prompt"),
                     reply_markup=driver_type_keyboard(chat_id))

@bot.message_handler(func=lambda msg: msg.text in ["📱 Livestream Setup", "📱 Transmisión", "📱 Go Live"])
def handle_livestream_booking(message):
    chat_id = message.chat.id
    pending_bookings[chat_id] = {'service_type': SERVICE_LIVESTREAM, 'details': {}}
    bot.send_message(chat_id, get_phrase(chat_id, "livestream_prompt"),
                     reply_markup=livestream_keyboard(chat_id))

@bot.message_handler(func=lambda msg: msg.text in ["📦 Delivery Runner", "📦 Mensajero", "📦 Run My Bag"])
def handle_delivery_booking(message):
    chat_id = message.chat.id
    pending_bookings[chat_id] = {'service_type': SERVICE_DELIVERY, 'details': {}}
    bot.send_message(chat_id, get_phrase(chat_id, "delivery_prompt"),
                     reply_markup=delivery_keyboard(chat_id))

@bot.message_handler(func=lambda msg: msg.text in ["Choose by date", "Nearest available", "ASAP (Walk-in)",
                                                 "Elegir fecha", "Próximo disponible", "Lo antes posible",
                                                 "Basic Vibes", "Pod Squad", "Trap Studio"])
def handle_slot_selection_method(message):
    chat_id = message.chat.id
    text = message.text
    
    if chat_id not in pending_bookings:
        bot.send_message(chat_id, get_phrase(chat_id, "no_service_selected"))
        return
        
    if "ASAP" in text or "Lo antes" in text:
        pending_bookings[chat_id]['details']['urgency'] = 'asap'
        bot.send_message(chat_id, get_phrase(chat_id, "asap_confirm_prompt"),
                         reply_markup=confirm_keyboard(chat_id))
    elif "Nearest" in text or "Próximo" in text:
        slots = find_nearest_slots()
        if not slots:
            bot.send_message(chat_id, get_phrase(chat_id, "no_slots_found"))
            return
        bot.send_message(chat_id, get_phrase(chat_id, "choose_slot"),
                         reply_markup=slots_keyboard(slots))
    else:
        # Date selection flow would go here
        pass

@bot.message_handler(func=lambda msg: re.match(r"⏱️ \w{3} \w{3} \d{2} • \d{2}:\d{2}[AP]M", msg.text))
def handle_slot_selection(message):
    chat_id = message.chat.id
    selected = message.text.replace("⏱️ ", "")
    
    if chat_id not in pending_bookings:
        bot.send_message(chat_id, get_phrase(chat_id, "no_service_selected"))
        return
        
    try:
        dt = datetime.strptime(selected, "%a %b %d • %I:%M%p")
        pending_bookings[chat_id]['details']['datetime'] = dt
        pending_bookings[chat_id]['details']['date'] = dt.strftime("%Y-%m-%d")
        pending_bookings[chat_id]['details']['time'] = dt.strftime("%H:%M")
        
        bot.send_message(
            chat_id,
            get_phrase(chat_id, "confirm_booking", 
                       service=pending_bookings[chat_id]['service_type'],
                       datetime=selected),
            reply_markup=confirm_keyboard(chat_id)
        )
    except ValueError:
        bot.send_message(chat_id, get_phrase(chat_id, "invalid_slot_format"))

@bot.message_handler(func=lambda msg: msg.text in ["✅ Confirm", "✅ Confirmar", "✅ Bet"])
def handle_confirmation(message):
    chat_id = message.chat.id
    user = message.from_user
    username = user.username or ""
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    
    if chat_id not in pending_bookings:
        bot.send_message(chat_id, get_phrase(chat_id, "no_pending_booking"))
        return
        
    booking = pending_bookings[chat_id]
    
    if booking['service_type'] == SERVICE_HAIR:
        # Handle hair service booking
        if 'datetime' in booking['details']:
            date = booking['details']['date']
            time = booking['details']['time']
            success = book_slot(date, time, name, "Hair Service", username=username, phone="")
            if success:
                bot.send_message(chat_id, get_phrase(chat_id, "booking_confirmed", 
                                                   service="hair service",
                                                   datetime=f"{date} {time}"),
                               reply_markup=main_menu_keyboard(chat_id))
            else:
                bot.send_message(chat_id, get_phrase(chat_id, "slot_taken"))
        else:
            # Handle ASAP bookings
            pass
            
    elif booking['service_type'] == SERVICE_DRIVER:
        # Handle driver service booking
        bot.send_message(chat_id, get_phrase(chat_id, "driver_confirmed"),
                         reply_markup=payment_keyboard(chat_id))
        
    elif booking['service_type'] == SERVICE_LIVESTREAM:
        # Handle livestream booking
        bot.send_message(chat_id, get_phrase(chat_id, "livestream_confirmed"),
                         reply_markup=payment_keyboard(chat_id))
        
    elif booking['service_type'] == SERVICE_DELIVERY:
        # Handle delivery booking
        bot.send_message(chat_id, get_phrase(chat_id, "delivery_confirmed"),
                         reply_markup=payment_keyboard(chat_id))
    
    pending_bookings.pop(chat_id, None)

@bot.message_handler(func=lambda msg: msg.text in ["❌ Cancel", "❌ Cancelar", "❌ Dead It"])
def handle_cancellation(message):
    chat_id = message.chat.id
    pending_bookings.pop(chat_id, None)
    bot.send_message(chat_id, get_phrase(chat_id, "booking_cancelled"),
                     reply_markup=main_menu_keyboard(chat_id))

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, get_phrase(chat_id, "unknown_command"),
                     reply_markup=main_menu_keyboard(chat_id))

if __name__ == "__main__":
    print("ATL5D Bot is running...")
    bot.infinity_polling()
