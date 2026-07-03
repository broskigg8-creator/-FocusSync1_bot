import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Stores focus states: (chat_id, user_id) -> True/False
focus_states = {}
# Stores user stats: (chat_id, user_id) -> count
user_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to FocusSync! Use /focus [minutes] to start a timed session.")

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Default to 25 minutes if no time is provided
    duration = 25
    if context.args:
        try:
            duration = int(context.args[0])
        except ValueError:
            pass

    focus_states[(chat_id, user.id)] = True
    await update.message.reply_text(f"🚀 {user.first_name} started a {duration}-minute focus session!")
    
    # Schedule the success message
    context.job_queue.run_once(success_callback, duration * 60, chat_id=chat_id, user_id=user.id, name=user.first_name)

async def success_callback(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    user_id = job.user_id
    
    if focus_states.get((chat_id, user_id)):
        focus_states[(chat_id, user_id)] = False
        # Update stats
        user_stats[(chat_id, user_id)] = user_stats.get((chat_id, user_id), 0) + 1
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Great work, {job.name}! Session complete.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    if focus_states.get((chat_id, user.id)):
        focus_states[(chat_id, user.id)] = False
        await update.message.reply_text(f"⚠️ {user.first_name}, your focus is broken! Get back to work.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    count = user_stats.get((chat_id, user.id), 0)
    await update.message.reply_text(f"📊 {user.first_name}, you have completed {count} focus sessions!")

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()
    
    # Ensure JobQueue is initialized
    job_queue = application.job_queue
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('focus', focus))
    application.add_handler(CommandHandler('stats', stats))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling()
