import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Stores state: { (chat_id, user_id): True }
focus_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to FocusSync! Use /focus to start your session. If you send any message while focusing, your focus will be broken.")

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Store state based on unique user+chat combo
    focus_states[(chat_id, user.id)] = True
    
    await update.message.reply_text(f"{user.first_name}, your focus session is active. Avoid messaging!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Check if this specific user is in a session in this specific chat
    if focus_states.get((chat_id, user.id)):
        # Reset state
        focus_states[(chat_id, user.id)] = False
        await update.message.reply_text(f"⚠️ {user.first_name}, your focus is broken! Get back to work.")

if __name__ == '__main__':
    # Ensure you have set this in Railway Variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('focus', focus))
    # Handles all non-command text
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling()
