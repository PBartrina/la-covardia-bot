import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from google.cloud import secretmanager
import functions_framework
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

# Get secrets from Secret Manager (recommended for production)
def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ['PROJECT_ID']}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# BOT_TOKEN = get_secret('telegram-bot-token')
# TARGET_GROUP_ID = get_secret('telegram-group-id')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TARGET_GROUP_ID = os.environ.get('TARGET_GROUP_ID')

# Rate limiting settings
MAX_MESSAGES = 5    # Maximum messages per time window
TIME_WINDOW = 60    # Time window in minutes (60 = 1 hour)
user_messages = defaultdict(list)  # Store user message timestamps

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola! Envia'm qualsevol missatge i el publicaré de manera anònima al grup. "
        "La teva identitat es mantindrà privada.\n\n"
        f"Límit: {MAX_MESSAGES} missatges cada hora."
    )

def check_rate_limit(user_id: int) -> bool:
    current_time = datetime.now()
    # Remove messages older than the time window
    user_messages[user_id] = [
        timestamp for timestamp in user_messages[user_id]
        if current_time - timestamp < timedelta(minutes=TIME_WINDOW)
    ]
    # Check if user has exceeded the limit
    if len(user_messages[user_id]) >= MAX_MESSAGES:
        return False
    # Add current message timestamp
    user_messages[user_id].append(current_time)
    return True

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only process private messages
    if update.message.chat.type != 'private':
        return
    
    try:
        # Check rate limit
        user_id = update.message.from_user.id
        if not check_rate_limit(user_id):
            remaining_minutes = TIME_WINDOW - int((datetime.now() - user_messages[user_id][0]).total_seconds() / 60)
            if remaining_minutes >= 60:
                time_msg = f"{remaining_minutes // 60} hora"
            else:
                time_msg = f"{remaining_minutes} minuts"
            
            await update.message.reply_text(
                f"Has superat el límit de {MAX_MESSAGES} missatges per hora. "
                f"Si us plau, espera {time_msg} més."
            )
            return

        # Forward the message content to the group
        if update.message.text:
            await context.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=update.message.text
            )
        elif update.message.photo:
            # Get the largest photo size
            photo = update.message.photo[-1]
            await context.bot.send_photo(
                chat_id=TARGET_GROUP_ID,
                photo=photo.file_id,
                caption=update.message.caption
            )
        elif update.message.document:
            await context.bot.send_document(
                chat_id=TARGET_GROUP_ID,
                document=update.message.document.file_id,
                caption=update.message.caption
            )
        
        # Confirm to the user that their message was sent
        messages_left = MAX_MESSAGES - len(user_messages[user_id])
        await update.message.reply_text(
            f"El teu missatge s'ha publicat anònimament! ✅\n"
            f"Et queden {messages_left} missatges en aquesta hora."
        )
        
    except Exception as e:
        await update.message.reply_text("Ho sento, hi ha hagut un error en publicar el teu missatge. Si us plau, torna-ho a provar.")
        print(f"Error: {str(e)}")

async def handle_update(update_dict):
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
    
    # Process update
    await application.initialize()
    await application.process_update(Update.de_json(update_dict, application.bot))

@functions_framework.http
def telegram_webhook(request):
    if request.method == "POST":
        update_dict = request.get_json()
        asyncio.run(handle_update(update_dict))
        return "ok"
    return "only POST requests are accepted"

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main() 