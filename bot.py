import os
from dotenv import load_dotenv
import unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Diccionario para almacenar el estado temporal de cada usuario
dynamic_state = {}

# Función para normalizar texto
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Función para obtener el menú principal
def obtener_menu_principal():
    keyboard = [
        [
            InlineKeyboardButton("📈 Información grupo premium", callback_data="info_premium"),
            InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Función para obtener el submenú de FAQ
def obtener_submenu_faq():
    keyboard = [
        [InlineKeyboardButton("📊 Porcentaje de ganancias", callback_data="ganancias")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="plataforma")],
        [InlineKeyboardButton("📌 Duda sobre un pick", callback_data="duda_pick")],
        [InlineKeyboardButton("🗨️ Otra pregunta", callback_data="otra_pregunta")],
        [InlineKeyboardButton("⬅️ Volver al menú principal", callback_data="volver_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dynamic_state.pop(user_id, None)
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=obtener_menu_principal())

# Manejo de callback queries (botones)
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "Sin username"
    nombre = query.from_user.full_name or "Sin nombre"

    if query.data == "info_premium":
        registro_url = (
            f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNplEEu22x"
            f"?notrack=true&telegram_id={user_id}"
        )
        mensaje = (
            "👋 <b>Hola!</b>\n\n"
            "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> (aproximadamente <b>25 USD</b>) mensuales.\n"
            "🎟️ Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
            f"📝 Llena este formulario para registrarte y realizar el pago:\n"
            f"<a href='{registro_url}'>{registro_url}</a>"
        )
        await query.edit_message_text(text=mensaje, parse_mode="HTML", reply_markup=obtener_menu_principal())

    elif query.data == "faq":
        await query.edit_message_text("📚 Selecciona una pregunta frecuente:", reply_markup=obtener_submenu_faq())

    elif query.data == "ganancias":
        mensaje = "📈 *PROMEDIO MENSUAL:* $11,773 ganados u 11.77 unidades ganadas\n💰 *TOTAL GENERAL:* $82,411 ganados u 82.41 unidades ganadas"
        await query.edit_message_text(text=mensaje, parse_mode="Markdown", reply_markup=obtener_submenu_faq())

    elif query.data == "plataforma":
        mensaje = "🏦 Usamos principalmente *Bet365* y *Playdoit*, pero puedes usar cualquier casa que permita apuestas a jugadores."
        await query.edit_message_text(text=mensaje, parse_mode="Markdown", reply_markup=obtener_submenu_faq())

    elif query.data == "duda_pick":
        dynamic_state[user_id] = "Duda sobre pick"
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick:")

    elif query.data == "otra_pregunta":
        dynamic_state[user_id] = "Otra pregunta general"
        await query.edit_message_text("🗨️ Por favor, escribe tu pregunta:")

    elif query.data == "volver_menu":
        await query.edit_message_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=obtener_menu_principal())

# Manejo de mensajes que no son comandos
async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Sin username"
    nombre = update.effective_user.full_name or "Sin nombre"
    mensaje = update.message.text.strip()

    if user_id in dynamic_state:
        motivo = dynamic_state.pop(user_id)
        texto = (
            f"📩 Nueva duda de cliente:\n"
            f"👤 Nombre: {nombre}\n"
            f"🆔 ID de Telegram: {user_id}\n"
            f"🔗 Usuario: @{username}\n"
            f"📌 Motivo: {motivo}\n"
            f"✉️ Mensaje: {mensaje}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=texto)
        await update.message.reply_text("Gracias, un administrador te responderá pronto.")
    else:
        await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=obtener_menu_principal())

# Main
if __name__ == "__main__":
    print("🚀 Bot de suscripción iniciando...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))
    print("✅ Bot en ejecución...")
    app.run_polling()