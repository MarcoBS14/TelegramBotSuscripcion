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
        [InlineKeyboardButton("📈 Suscripción inmediata — Pago en línea", callback_data="info_premium")],
        [InlineKeyboardButton("👨‍💼 Pago asistido — Enlace por asesor", callback_data="pago_asesor")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="preguntas_frecuentes")]
    ])

# Submenú actualizads
def faq_menu_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 % de ganancias", callback_data="faq_ganancias")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="faq_plataformas")],
        [InlineKeyboardButton("💬 Contactar soporte", url="https://t.me/mmsportplays")],
        [InlineKeyboardButton("🔙 Menú principal", callback_data="volver_inicio")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_home = (
        "👋 ¿Cómo puedo ayudarte hoy?\n\n"
        "Puedes elegir entre dos formas de suscripción al grupo premium:\n"
        "• Inmediata en línea (por este bot).\n"
        "• Asistida por un asesor (contacto directo)."
    )
    await update.message.reply_text(texto_home, reply_markup=main_menu_inline())

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
            "🧾 <b>Suscripción inmediata — Pago en línea</b>\n\n"
            "💸 Costo de entrada al grupo: <b>499 pesos mexicanos</b> (aprox. <b>25 USD</b>) mensuales.\n"
            "🔒 Pago seguro en línea a través de nuestro formulario.\n"
            "✅ Una vez acreditado el pago, se te agrega automáticamente al grupo premium.\n\n"
            f"📝 Completa tu registro y realiza el pago en el siguiente enlace:\n"
            f"<a href='{registro_url}'>{registro_url}</a>"
        )
        await query.edit_message_text(text=texto, parse_mode="HTML", reply_markup=main_menu_inline())

    elif query.data == "pago_asesor":
        texto = (
            "👨‍💼 <b>Pago asistido — Enlace por asesor</b>\n\n"
            "💸 Costo de entrada al grupo: <b>499 pesos mexicanos</b> (aprox. <b>25 USD</b>) mensuales.\n"
            "🔒 Es el mismo formulario seguro que en la suscripción inmediata.\n"
            "👨‍💼 En este caso, un asesor te compartirá el enlace y resolverá cualquier duda.\n\n"
            "Escríbele con el mensaje:\n"
            "<i>“Quiero suscribirme al grupo premium.”</i>\n\n"
            "En breve el asesor te atenderá."
        )
        reply = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Contactar asesor", url="https://t.me/mmsportplays")],
            [InlineKeyboardButton("🔙 Menú principal", callback_data="volver_inicio")]
        ])
        await query.edit_message_text(text=texto, parse_mode="HTML", reply_markup=reply)

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
        texto_home = (
            "👋 ¿Cómo puedo ayudarte hoy?\n\n"
            "Puedes elegir entre dos formas de suscripción al grupo premium:\n"
            "• Inmediata en línea (por este bot).\n"
            "• Asistida por un asesor (contacto directo)."
        )
        await query.edit_message_text(text=texto_home, reply_markup=main_menu_inline())

# Manejar mensajes de texto que no sean comandos
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_home = (
        "👋 ¿Cómo puedo ayudarte hoy?\n\n"
        "Puedes elegir entre dos formas de suscripción al grupo premium:\n"
        "• Inmediata en línea (por este bot).\n"
        "• Asistida por un asesor (contacto directo)."
    )
    await update.message.reply_text(texto_home, reply_markup=main_menu_inline())

# Ejecutar bot
if __name__ == "__main__":
    print("✅ Bot corriendo en modo polling...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()