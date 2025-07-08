import os
import unicodedata
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
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

# Diccionario temporal para estado de conversación
dynamic_state = {}

# Función para normalizar el texto
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# --- Menús con Inline Keyboards ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📈 Información grupo premium", callback_data="info_premium")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_faq_menu():
    keyboard = [
        [InlineKeyboardButton("📊 % de ganancias", callback_data="faq_ganancias")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="faq_plataforma")],
        [InlineKeyboardButton("📩 Duda sobre pick", callback_data="faq_duda_pick")],
        [InlineKeyboardButton("💬 Otra pregunta", callback_data="faq_otra")],
        [InlineKeyboardButton("🔙 Volver al inicio", callback_data="volver")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dynamic_state.pop(update.effective_user.id, None)
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=get_main_menu())

# --- Manejo de botones Inline ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or "Sin username"
    nombre = query.from_user.full_name or "Sin nombre"

    await query.answer()

    if query.data == "info_premium":
        registro_url = (
            f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNpIEEu22x"
            f"?notrack=true&telegram_id={user_id}"
        )
        await query.edit_message_text(
            text=(
                "👋 <b>Hola!</b>\n\n"
                "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> "
                "(aproximadamente <b>25 USD</b>) mensuales.\n"
                "🎟️ Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
                f"📝 Llena este formulario para registrarte y realizar el pago:\n"
                f"<a href='{registro_url}'>{registro_url}</a>\n\n"
            ),
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )

    elif query.data == "faq":
        await query.edit_message_text("❓ Selecciona una pregunta frecuente:", reply_markup=get_faq_menu())

    elif query.data == "faq_ganancias":
        await query.edit_message_text(
            text=(
                "📈 <b>PROMEDIO MENSUAL:</b> $11,773 ganados u 11.77 unidades ganadas\n"
                "💰 <b>TOTAL GENERAL:</b> $82,411 ganados u 82.41 unidades ganadas"
            ),
            parse_mode="HTML",
            reply_markup=get_faq_menu()
        )

    elif query.data == "faq_plataforma":
        await query.edit_message_text(
            text="🏦 Usamos principalmente <b>Bet365</b> y <b>Playdoit</b>, pero puedes usar cualquier casa que permita apuestas a jugadores.",
            parse_mode="HTML",
            reply_markup=get_faq_menu()
        )

    elif query.data == "faq_duda_pick":
        dynamic_state[user_id] = "Duda sobre pick"
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick.")

    elif query.data == "faq_otra":
        dynamic_state[user_id] = "Otra pregunta general"
        await query.edit_message_text("🗨️ Por favor, escribe tu pregunta.")

    elif query.data == "volver":
        await query.edit_message_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=get_main_menu())

# --- Manejo de texto libre ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.effective_user.id)
    username = update.effective_user.username or "Sin username"
    nombre = update.effective_user.full_name or "Sin nombre"
    text_raw = update.message.text.strip()

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
        await update.message.reply_text("Gracias, un administrador te responderá pronto.")
    else:
        await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=get_main_menu())

# --- Lanzar el bot ---
if __name__ == "__main__":
    print("🔄 Iniciando bot en modo polling...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot corriendo correctamente...")
    app.run_polling()