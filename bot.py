import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dictionary to track focus state: {user_id: True/False}
focus_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to FocusSync! Use /focus to start your session.")

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    focus_states[user_id] = True
    await update.message.reply_text("Focus session started. Do not message me until you are finished!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if focus_states.get(user_id):
        await update.message.reply_text("⚠️ FOCUS BROKEN! Get back to work!")
        focus_states[user_id] = False
    else:
        await update.message.reply_text("You are currently idle. Type /focus to start.")

if __name__ == '__main__':
    # Use environment variable for token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('focus', focus))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling()
