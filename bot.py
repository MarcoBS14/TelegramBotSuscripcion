import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Teclados ---
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Información sobre el grupo premium", callback_data="info")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq")]
    ])

def faq_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Porcentaje de ganancias", callback_data="faq_ganancias")],
        [InlineKeyboardButton("🏦 Plataforma de apuestas", callback_data="faq_plataforma")],
        [InlineKeyboardButton("📬 Duda sobre pick", callback_data="faq_pick")],
        [InlineKeyboardButton("💬 Otra pregunta", callback_data="faq_otra")],
        [InlineKeyboardButton("🔙 Menú principal", callback_data="menu_principal")]
    ])

def back_to_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Menú principal", callback_data="menu_principal")]
    ])

# --- Estado dinámico ---
dynamic_state = {}

# --- Funciones principales ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=main_menu_keyboard())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Menú principal
    if query.data == "menu_principal":
        await query.edit_message_text("👋 ¿Cómo puedo ayudarte hoy?", reply_markup=main_menu_keyboard())

    elif query.data == "info":
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
            reply_markup=back_to_main_menu_keyboard(),
            parse_mode="HTML"
        )

    elif query.data == "faq":
        await query.edit_message_text("❓ Selecciona una pregunta frecuente:", reply_markup=faq_menu_keyboard())

    elif query.data == "faq_ganancias":
        await query.edit_message_text("📈 *PROMEDIO MENSUAL:* $11,773 ganados u 11.77 unidades ganadas\n💰 *TOTAL GENERAL:* $82,411 ganados u 82.41 unidades ganadas", parse_mode="Markdown", reply_markup=faq_menu_keyboard())

    elif query.data == "faq_plataforma":
        await query.edit_message_text("🏦 Usamos principalmente *Bet365* y *Playdoit*, pero puedes usar cualquier casa que permita apuestas a jugadores.", parse_mode="Markdown", reply_markup=faq_menu_keyboard())

    elif query.data == "faq_pick":
        await query.edit_message_text("📝 Por favor, escribe tu duda sobre algún pick.", reply_markup=back_to_main_menu_keyboard())

    elif query.data == "faq_otra":
        await query.edit_message_text("💬 Por favor, escribe tu pregunta general.", reply_markup=back_to_main_menu_keyboard())

# --- Arranque del bot ---
if __name__ == "__main__":
    print("✅ Bot de información y FAQ corriendo...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()