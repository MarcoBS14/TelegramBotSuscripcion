import os
import unicodedata
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Estado temporal para preguntas abiertas
dynamic_state = {}

# Normalizar texto
def normalizar(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Menú principal con inline keyboard
def obtener_menu_principal():
    keyboard = [
        [
            InlineKeyboardButton("📈 Información", callback_data="info_premium"),
            InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Submenú FAQ
def obtener_menu_faq():
    keyboard = [
        [InlineKeyboardButton("📈 Porcentaje de ganancias", callback_data="porcentaje")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="plataforma")],
        [InlineKeyboardButton("📈 Duda de pick", callback_data="duda_pick")],
        [InlineKeyboardButton("❓ Otra pregunta", callback_data="otra_pregunta")],
        [InlineKeyboardButton("🔙 Regresar al menú", callback_data="volver_menu")]
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

# Manejador de botones
async def manejar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nombre = query.from_user.full_name or "Sin nombre"
    username = query.from_user.username or "Sin username"

    if query.data == "info_premium":
        url = f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNpIEEu22x?notrack=true&telegram_id={user_id}"
        texto = (
            "👋 <b>Hola!</b>\n\n"
            "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> (aproximadamente <b>25 USD</b>) mensuales.\n"
            "💼 Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
            f"📄 Llena este formulario para registrarte y realizar el pago:\n<a href='{url}'>{url}</a>"
        )
        await context.bot.send_message(chat_id=query.message.chat_id, text=texto, parse_mode="HTML", reply_markup=obtener_menu_principal())

    elif query.data == "faq":
        await context.bot.send_message(chat_id=query.message.chat_id, text="📊 Preguntas frecuentes:", reply_markup=obtener_menu_faq())

    elif query.data == "porcentaje":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📉 <b>PROMEDIO MENSUAL:</b> $11,773 ganados u 11.77 unidades ganadas\n💰 <b>TOTAL GENERAL:</b> $82,411 ganados u 82.41 unidades ganadas",
            parse_mode="HTML",
            reply_markup=obtener_menu_faq()
        )

    elif query.data == "plataforma":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🏦 Usamos principalmente *Bet365* y *Playdoit*, pero puedes usar cualquier casa que permita apuestas a jugadores.",
            parse_mode="Markdown",
            reply_markup=obtener_menu_faq()
        )

    elif query.data == "duda_pick":
        dynamic_state[user_id] = "Duda sobre pick"
        await context.bot.send_message(chat_id=query.message.chat_id, text="📝 Por favor, escribe tu duda sobre el pick.")

    elif query.data == "otra_pregunta":
        dynamic_state[user_id] = "Otra pregunta general"
        await context.bot.send_message(chat_id=query.message.chat_id, text="💬 Por favor, escribe tu pregunta.")

    elif query.data == "volver_menu":
        await context.bot.send_message(chat_id=query.message.chat_id, text="👋 ¿Cómo puedo ayudarte hoy?", reply_markup=obtener_menu_principal())

# Manejador de mensajes escritos
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.effective_user.id)
    username = update.effective_user.username or "Sin username"
    nombre = update.effective_user.full_name or "Sin nombre"
    text_raw = update.message.text.strip()
    text = normalizar(text_raw)

    if user_id in dynamic_state:
        motivo = dynamic_state.pop(user_id)
        mensaje = (
            f"📧 Nueva duda de cliente:\n"
            f"👤 Nombre: {nombre}\n"
            f"🆔 ID de Telegram: {user_id}\n"
            f"🔗 Usuario: @{username}\n"
            f"📌 Motivo: {motivo}\n"
            f"✉️ Mensaje: {text_raw}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensaje)
        await update.message.reply_text("Gracias, un administrador te responderá pronto.", reply_markup=obtener_menu_principal())
    else:
        await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=obtener_menu_principal())

# Ejecutar bot
if __name__ == "__main__":
    print("🔄 Iniciando bot en modo polling...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(manejar_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    print("✅ Bot corriendo correctamente...")
    app.run_polling()
