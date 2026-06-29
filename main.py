from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

from config import TOKEN, ADMIN_ID


# ---------------- STORAGE ----------------
USER_MODE = {}
MESSAGE_MAP = {}


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🕶 پیام ناشناس", callback_data="anon")],
        [InlineKeyboardButton("👤 پیام با یوزرنیم", callback_data="user")]
    ]

    await update.message.reply_text(
        "سلام 👋\nیکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- BUTTON ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    USER_MODE[query.from_user.id] = query.data

    await query.message.reply_text("پیامت رو بنویس ✍️")


# ---------------- MESSAGE ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    mode = USER_MODE.get(user.id)

    if not mode:
        await update.message.reply_text("اول /start رو بزن 👈")
        return

    text = update.message.text

    if mode == "anon":
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🕶 ناشناس:\n\n{text}"
        )

    else:
        username = user.username or "بدون یوزرنیم"
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"👤 @{username}:\n\n{text}"
        )

    MESSAGE_MAP[sent.message_id] = user.id
    USER_MODE[user.id] = None

    await update.message.reply_text("ارسال شد ✔️")


# ---------------- ADMIN REPLY ----------------
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    msg_id = update.message.reply_to_message.message_id
    user_id = MESSAGE_MAP.get(msg_id)

    if user_id:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📩 پاسخ ادمین:\n\n{update.message.text}"
        )


# ---------------- MAIN ----------------
def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, admin_reply))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()