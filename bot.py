import os
import unicodedata
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Normalizar texto
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Menú principal
def main_menu_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Información grupo premium", callback_data="info_premium")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="preguntas_frecuentes")]
    ])

# Submenú actualizad
def faq_menu_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 % de ganancias", callback_data="faq_ganancias")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="faq_plataformas")],
        [InlineKeyboardButton("💬 Contactar soporte", url="https://t.me/MarcoBS14")],
        [InlineKeyboardButton("🔙 Menú principal", callback_data="volver_inicio")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=main_menu_inline())

# Botones Inline
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "info_premium":
        registro_url = (
            f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNplEEu22x"
            f"?notrack=true&telegram_id={user_id}"
        )
        texto = (
            "👋 <b>Hola!</b>\n\n"
            "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> (aproximadamente <b>25 USD</b>) mensuales.\n"
            "🧾 Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
            f"📝 Llena este formulario para registrarte y realizar el pago:\n"
            f"<a href='{registro_url}'>{registro_url}</a>"
        )
        await query.edit_message_text(text=texto, parse_mode="HTML", reply_markup=main_menu_inline())

    elif query.data == "preguntas_frecuentes":
        await query.edit_message_text("❓ Selecciona una pregunta frecuente:", reply_markup=faq_menu_inline())

    elif query.data == "faq_ganancias":
        texto = (
            "📈 <b>PROMEDIO MENSUAL:</b> $11,773 ganados u 11.77 unidades ganadas\n"
            "💰 <b>TOTAL GENERAL:</b> $82,411 ganados u 82.41 unidades ganadas"
        )
        await query.edit_message_text(text=texto, parse_mode="HTML", reply_markup=faq_menu_inline())

    elif query.data == "faq_plataformas":
        texto = (
            "🏦 Usamos principalmente <b>Bet365</b> y <b>Playdoit</b>, pero puedes usar cualquier casa que permita apuestas a jugadores."
        )
        await query.edit_message_text(text=texto, parse_mode="HTML", reply_markup=faq_menu_inline())

    elif query.data == "volver_inicio":
        await query.edit_message_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=main_menu_inline())

# Manejar mensajes de texto que no sean comandos
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=main_menu_inline())

# Ejecutar bot
if __name__ == "__main__":
    print("✅ Bot corriendo en modo polling...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()