import os
from dotenv import load_dotenv
import unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Estados temporales
dynamic_state = {}

# Normalizar texto
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1️⃣ Info grupo premium", callback_data="grupo")],
        [InlineKeyboardButton("2️⃣ Preguntas frecuentes", callback_data="faq")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=reply_markup)

# Manejador de botones
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.from_user.id)
    username = query.from_user.username or "Sin username"
    nombre = query.from_user.full_name or "Sin nombre"

    if query.data == "grupo":
        registro_url = (
            f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNplEEu22x"
            f"?notrack=true&telegram_id={user_id}"
        )
        await query.edit_message_text(
            text=(
                "👋 <b>Hola!</b>\n\n"
                "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> (aproximadamente <b>25 USD</b>) mensuales.\n"
                "🎟️ Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
                f"📝 Llena este formulario para registrarte y realizar el pago:\n"
                f"<a href='{registro_url}'>{registro_url}</a>"
            ),
            parse_mode="HTML"
        )

    elif query.data == "faq":
        keyboard = [
            [InlineKeyboardButton("📈 % Ganancias", callback_data="ganancias")],
            [InlineKeyboardButton("🏦 Plataforma apuestas", callback_data="plataforma")],
            [InlineKeyboardButton("📊 Duda de pick", callback_data="pick")],
            [InlineKeyboardButton("❓ Otra pregunta", callback_data="otra")]
        ]
        await query.edit_message_text("Selecciona una opción frecuente:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "ganancias":
        await query.edit_message_text("📈 *PROMEDIO MENSUAL:* $11,773 ganados u 11.77 unidades ganadas\n💰 *TOTAL GENERAL:* $82,411 ganados u 82.41 unidades ganadas", parse_mode="Markdown")

    elif query.data == "plataforma":
        await query.edit_message_text("🏦 Usamos principalmente *Bet365* y *Playdoit*, pero puedes usar cualquier casa que permita apuestas a jugadores.", parse_mode="Markdown")

    elif query.data == "pick":
        dynamic_state[user_id] = "Duda sobre pick"
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick.")

    elif query.data == "otra":
        dynamic_state[user_id] = "Otra pregunta general"
        await query.edit_message_text("🗨️ Por favor, escribe tu pregunta.")

# Manejador de texto libre (respuesta personalizada)
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
        await start(update, context)

# Lanzar el bot
if __name__ == "__main__":
    print("✅ Bot corriendo con Inline Keyboards...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()