from telebot import types
from datetime import datetime
from translations import TRANSLATIONS
from users import get_user_lang

def language_keyboard():
    """Returns language selection keyboard with ATL Gen-Z options"""
    options = {
        "🇺🇸 English": "en",
        "🇪🇸 Español": "es",
        "🔥 ATL Slang": "atl"  # Added for Atlanta urban dialect
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for label in options:
        markup.add(label)
    return markup, options

def main_menu_keyboard(chat_id):
    """ATL5D main menu with Gen-Z services"""
    lang = get_user_lang(chat_id)

    buttons = {
        "en": ["💈 Book Barber", "🚗 Get Driver", "📱 Livestream Setup", "📦 Delivery Runner", "⚙️ Settings"],
        "es": ["💈 Barbero", "🚗 Conductor", "📱 Transmisión", "📦 Mensajero", "⚙️ Configuración"],
        "atl": ["💈 Fade Me Up", "🚗 Pull Up", "📱 Go Live", "📦 Run My Bag", "⚙️ Fixins"]  # ATL slang versions
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Organize in two columns for better mobile UX
    row1 = [buttons.get(lang, buttons["en"])[0], buttons.get(lang, buttons["en"])[1]]
    row2 = [buttons.get(lang, buttons["en"])[2], buttons.get(lang, buttons["en"])[3]]
    markup.add(*row1)
    markup.add(*row2)
    markup.add(buttons.get(lang, buttons["en"])[4])  # Settings always last
    return markup

def driver_type_keyboard(chat_id):
    """Keyboard for ATL driver services"""
    lang = get_user_lang(chat_id)
    
    options = {
        "en": ["🚖 Regular Ride", "💎 Luxury Ride", "📦 Package Delivery", "🍃 420 Friendly"],
        "es": ["🚖 Viaje normal", "💎 Viaje de lujo", "📦 Entrega de paquete", "🍃 420 Amigable"],
        "atl": ["🚖 Regular Pull", "💎 Drip Ride", "📦 Run My Bag", "🍃 Zooted Driver"]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*options.get(lang, options["en"]))
    return markup

def livestream_keyboard(chat_id):
    """Keyboard for ATL livestream services"""
    lang = get_user_lang(chat_id)
    
    options = {
        "en": ["🎥 Basic Setup", "🎤 Podcast Ready", "🎶 Music Studio", "📱 Phone Stream"],
        "es": ["🎥 Configuración básica", "🎤 Listo para podcast", "🎶 Estudio de música", "📱 Transmisión por teléfono"],
        "atl": ["🎥 Basic Vibes", "🎤 Pod Squad", "🎶 Trap Studio", "📱 IG Live Setup"]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*options.get(lang, options["en"]))
    markup.add(cancel_label(lang))
    return markup

def delivery_keyboard(chat_id):
    """Keyboard for ATL delivery services"""
    lang = get_user_lang(chat_id)
    
    options = {
        "en": ["🍔 Food Run", "💊 Pharmacy", "📦 Package", "🍃 Special Request"],
        "es": ["🍔 Comida", "💊 Farmacia", "📦 Paquete", "🍃 Petición especial"],
        "atl": ["🍔 Food Dash", "💊 Meds Move", "📦 Pack Drop", "🍃 Za Run"]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*options.get(lang, options["en"]))
    markup.add(cancel_label(lang))
    return markup

def urgency_keyboard(chat_id):
    """Keyboard for service urgency (Gen-Z style)"""
    lang = get_user_lang(chat_id)
    
    options = {
        "en": ["🚨 ASAP (Right Now)", "⏰ Scheduled", "💤 Later Today"],
        "es": ["🚨 Ahora mismo", "⏰ Programado", "💤 Más tarde"],
        "atl": ["🚨 RN!!!", "⏰ On Time", "💤 Later Sk8r"]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*options.get(lang, options["en"]))
    return markup

def cancel_label(lang):
    """Helper function for cancel button text"""
    return {
        "en": "❌ Cancel",
        "es": "❌ Cancelar",
        "atl": "❌ Dead It"
    }.get(lang, "❌ Cancel")

def cancel_keyboard(chat_id):
    """Gen-Z cancel keyboard"""
    lang = get_user_lang(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(cancel_label(lang))
    return markup

def confirm_keyboard(chat_id):
    """Gen-Z confirmation keyboard"""
    lang = get_user_lang(chat_id)
    
    options = {
        "en": ["✅ Confirm", "✏️ Edit", "❌ Cancel"],
        "es": ["✅ Confirmar", "✏️ Editar", "❌ Cancelar"],
        "atl": ["✅ Bet", "✏️ Fix It", "❌ Nah"]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*options.get(lang, options["en"]))
    return markup

def payment_keyboard(chat_id):
    """Keyboard for ATL payment options"""
    lang = get_user_lang(chat_id)
    
    options = {
        "en": ["💳 Card", "📱 Cash App", "💰 Zelle", "🪙 Crypto"],
        "es": ["💳 Tarjeta", "📱 Cash App", "💰 Zelle", "🪙 Cripto"],
        "atl": ["💳 Plastic", "📱 CashApp Me", "💰 Zelle Gang", "🪙 Bitcoin Bih"]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*options.get(lang, options["en"]))
    return markup

def slots_keyboard(slots: list):
    """Gen-Z styled time slots"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for slot in slots:
        dt = datetime.strptime(f"{slot[0]} {slot[1]}", "%Y-%m-%d %H:%M")
        label = dt.strftime("%a %b %d • %I:%M%p")
        markup.add(f"⏱️ {label}")
    return markup
