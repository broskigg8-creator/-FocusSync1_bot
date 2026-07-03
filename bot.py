import os
import psycopg2
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
# Get the database URL from Railway Variables
DATABASE_URL = os.getenv('DATABASE_URL')

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats (chat_id BIGINT, user_id BIGINT, count INTEGER, PRIMARY KEY (chat_id, user_id))''')
    conn.commit()
    conn.close()

def update_stats(chat_id, user_id):
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT INTO stats (chat_id, user_id, count) VALUES (%s, %s, 1) ON CONFLICT (chat_id, user_id) DO UPDATE SET count = stats.count + 1", (chat_id, user_id))
    conn.commit()
    conn.close()

def get_stats(chat_id, user_id):
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT count FROM stats WHERE chat_id=%s AND user_id=%s", (chat_id, user_id))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

init_db()

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🚀 {user.first_name} started a 25-minute focus session!")
    context.job_queue.run_once(lambda ctx: (update_stats(chat_id, user.id), 
        ctx.bot.send_message(chat_id=chat_id, text=f"✅ Great work, {user.first_name}! Session complete.")), 25 * 60)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = get_stats(update.effective_chat.id, update.effective_user.id)
    await update.message.reply_text(f"📊 {update.effective_user.first_name}, you have completed {count} focus sessions!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(CommandHandler('focus', focus))
    application.add_handler(CommandHandler('stats', stats))
    application.run_polling()
