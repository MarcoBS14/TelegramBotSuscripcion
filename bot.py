import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1. Información sobre el grupo premium", callback_data="info")],
        [InlineKeyboardButton("2. Preguntas frecuentes", callback_data="faq")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=reply_markup)

# Manejo de botones
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "info":
        registro_url = (
            f"https://api.buclecompany.com/widget/form/K4jL17NuYNDNplEEu22x"
            f"?notrack=true&telegram_id={user_id}"
        )
        await query.edit_message_text(
            "👋 <b>Hola!</b>\n\n"
            "💸 El costo de entrada al grupo es de <b>499 pesos mexicanos</b> (~25 USD) mensuales.\n"
            "🎟️ Una vez realizado el pago, se te agrega directamente al grupo premium.\n\n"
            f"📝 Llena este formulario para registrarte:\n"
            f"<a href='{registro_url}'>{registro_url}</a>",
            parse_mode="HTML"
        )

    elif query.data == "faq":
        keyboard = [
            [InlineKeyboardButton("1. Porcentaje de ganancias", callback_data="ganancias")],
            [InlineKeyboardButton("2. Plataforma de apuestas", callback_data="plataforma")],
            [InlineKeyboardButton("3. Duda de pick", callback_data="duda_pick")],
            [InlineKeyboardButton("4. Otra pregunta", callback_data="otra")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="volver")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📌 Preguntas frecuentes:", reply_markup=reply_markup)

    elif query.data == "ganancias":
        await query.edit_message_text(
            "📈 *PROMEDIO MENSUAL:* $11,773 ganados u 11.77 unidades ganadas\n"
            "💰 *TOTAL GENERAL:* $82,411 ganados u 82.41 unidades ganadas",
            parse_mode="Markdown"
        )

    elif query.data == "plataforma":
        await query.edit_message_text(
            "🏦 Usamos principalmente *Bet365* y *Playdoit*, pero puedes usar cualquier casa que permita apuestas a jugadores.",
            parse_mode="Markdown"
        )

    elif query.data == "duda_pick":
        context.user_data["pregunta_personalizada"] = "Duda sobre pick"
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick.")

    elif query.data == "otra":
        context.user_data["pregunta_personalizada"] = "Otra pregunta general"
        await query.edit_message_text("🗨️ Por favor, escribe tu pregunta.")

    elif query.data == "volver":
        await start(update, context)

# Manejo de preguntas personalizadas
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nombre = update.effective_user.full_name
    username = update.effective_user.username or "Sin username"
    texto = update.message.text.strip()

    motivo = context.user_data.get("pregunta_personalizada")
    if motivo:
        mensaje = (
            f"📩 Nueva duda de cliente:\n"
            f"👤 Nombre: {nombre}\n"
            f"🔗 Usuario: @{username}\n"
            f"🆔 Telegram ID: {user_id}\n"
            f"📌 Motivo: {motivo}\n"
            f"✉️ Mensaje: {texto}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensaje)
        await update.message.reply_text("Gracias, un administrador te responderá pronto.")
        context.user_data.pop("pregunta_personalizada")
    else:
        await update.message.reply_text("👋 Usa el menú para navegar. Escribe /start para volver.")

# Ejecutar bot
if __name__ == "__main__":
    print("🔄 Iniciando bot en modo polling...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot corriendo correctamente...")
    app.run_polling()