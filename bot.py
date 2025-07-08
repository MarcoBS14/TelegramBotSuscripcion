import os
import unicodedata
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Estados temporales para preguntas
dynamic_state = {}

# Función para normalizar texto (quita tildes y pone en minúsculas)
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Menú principal en formato Inline Keyboard (una columna para celulares)
def obtener_menu_principal():
    keyboard = [
        [InlineKeyboardButton("📈 Información grupo premium", callback_data="info_premium")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Submenú FAQ con botón de regreso
def obtener_menu_faq():
    keyboard = [
        [InlineKeyboardButton("📊 Porcentaje de ganancias", callback_data="faq_ganancias")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="faq_plataforma")],
        [InlineKeyboardButton("📋 Duda de pick", callback_data="faq_pick")],
        [InlineKeyboardButton("❔ Otra pregunta", callback_data="faq_otro")],
        [InlineKeyboardButton("🔙 Volver al menú principal", callback_data="volver_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.effective_user.id)
    dynamic_state.pop(user_id, None)
    await update.message.reply_text(
        "👋 ¿Cómo puedo ayudarte hoy?",
        reply_markup=obtener_menu_principal()
    )

# Botón Inline (callback queries)
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.from_user.id)
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
        await query.edit_message_text(text=mensaje, parse_mode="HTML")

    elif query.data == "faq":
        await query.edit_message_text("📌 Preguntas frecuentes:", reply_markup=obtener_menu_faq())

    elif query.data == "faq_ganancias":
        await query.edit_message_text(
            "📈 *PROMEDIO MENSUAL:* $11,773 ganados u 11.77 unidades ganadas\n"
            "💰 *TOTAL GENERAL:* $82,411 ganados u 82.41 unidades ganadas",
            parse_mode="Markdown"
        )

    elif query.data == "faq_plataforma":
        await query.edit_message_text(
            "🏦 Usamos principalmente *Bet365* y *Playdoit*, pero puedes usar cualquier casa que permita apuestas a jugadores.",
            parse_mode="Markdown"
        )

    elif query.data == "faq_pick":
        dynamic_state[user_id] = "Duda sobre pick"
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick.")

    elif query.data == "faq_otro":
        dynamic_state[user_id] = "Otra pregunta general"
        await query.edit_message_text("🗨️ Por favor, escribe tu pregunta.")

    elif query.data == "volver_menu":
        await query.edit_message_text(
            "👋 ¿Cómo puedo ayudarte hoy?",
            reply_markup=obtener_menu_principal()
        )

# Manejo de mensajes de texto (respuestas personalizadas)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.effective_user.id)
    username = update.effective_user.username or "Sin username"
    nombre = update.effective_user.full_name or "Sin nombre"
    text_raw = update.message.text.strip()

    # Si está esperando respuesta personalizada
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
        return

    # Si no hay estado, mostrar menú principal nuevamente
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=obtener_menu_principal())

# Iniciar aplicación
if __name__ == "__main__":
    print("🚀 Bot en ejecución...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()