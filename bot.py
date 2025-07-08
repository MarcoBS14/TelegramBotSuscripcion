import os
import unicodedata
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Estados temporales
dynamic_state = {}

# Normalizar texto
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Menú principal inline
def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📈 Información grupo premium", callback_data="info_premium"),
            InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="preguntas")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Submenú de preguntas frecuentes
def get_faq_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Porcentaje de ganancias", callback_data="porcentaje")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="plataforma")],
        [InlineKeyboardButton("🎯 Duda de pick", callback_data="duda_pick")],
        [InlineKeyboardButton("🗨️ Otra pregunta", callback_data="otra_pregunta")],
        [InlineKeyboardButton("🔙 Regresar al menú", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Botón para regresar al menú
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "👋 ¿Cómo puedo ayudarte hoy?",
        reply_markup=get_main_menu()
    )

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.effective_user.id)
    dynamic_state.pop(user_id, None)
    await update.message.reply_text(
        "👋 ¿Cómo puedo ayudarte hoy?",
        reply_markup=get_main_menu()
    )

# Manejo de botones inline
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "Sin username"
    nombre = query.from_user.full_name or "Sin nombre"

    data = query.data

    if data == "menu":
        await show_main_menu(update, context)

    elif data == "info_premium":
        registro_url = (
            f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNpIEEu22x?notrack=true&telegram_id={user_id}"
        )
        mensaje = (
            "👋 <b>Hola!</b>\n\n"
            "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> (aproximadamente <b>25 USD</b>) mensuales.\n"
            "🎟️ Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
            f"📝 Llena este formulario para registrarte y realizar el pago:\n"
            f"<a href='{registro_url}'>{registro_url}</a>\n\n"
        )
        await query.edit_message_text(mensaje, parse_mode="HTML", reply_markup=get_main_menu())

    elif data == "preguntas":
        await query.edit_message_text("📌 Preguntas frecuentes:", reply_markup=get_faq_menu())

    elif data == "porcentaje":
        mensaje = (
            "📈 <b>PROMEDIO MENSUAL:</b> $11,773 ganados u 11.77 unidades ganadas\n"
            "💰 <b>TOTAL GENERAL:</b> $82,411 ganados u 82.41 unidades ganadas"
        )
        await query.edit_message_text(mensaje, parse_mode="HTML", reply_markup=get_faq_menu())

    elif data == "plataforma":
        mensaje = (
            "🏦 Usamos principalmente <b>Bet365</b> y <b>Playdoit</b>,\n"
            "pero puedes usar cualquier casa que permita apuestas a jugadores."
        )
        await query.edit_message_text(mensaje, parse_mode="HTML", reply_markup=get_faq_menu())

    elif data == "duda_pick":
        dynamic_state[user_id] = "Duda sobre pick"
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick.")

    elif data == "otra_pregunta":
        dynamic_state[user_id] = "Otra pregunta general"
        await query.edit_message_text("🗨️ Por favor, escribe tu pregunta.")

# Manejo de mensajes de texto para dudas personalizadas
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.effective_user.id)
    username = update.effective_user.username or "Sin username"
    nombre = update.effective_user.full_name or "Sin nombre"
    text_raw = update.message.text.strip()
    text = normalizar(text_raw)

    if user_id in dynamic_state:
        motivo = dynamic_state.pop(user_id)
        mensaje = (
            f"📩 Nueva duda de cliente:\n"
            f"👤 Nombre: {nombre}\n"
            f"🆔 ID de Telegram: {user_id}\n"
            f"🔗 Usuario: @{username}\n"
            f"📌 Motivo: {motivo}\n"
            f"✉️ Mensaje: {text_raw}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensaje)
        await update.message.reply_text("✅ Gracias, un administrador te responderá pronto.")
    else:
        # Redirigir al menú si escribe algo fuera de contexto
        await update.message.reply_text(
            "👋 ¿Cómo puedo ayudarte hoy?",
            reply_markup=get_main_menu()
        )

# Ejecutar bot
if __name__ == "__main__":
    print("🔄 Iniciando bot en modo polling...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot corriendo correctamente...")
    app.run_polling()