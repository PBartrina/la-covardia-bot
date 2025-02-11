import os
import functions_framework
from telegram import Update, Bot
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TARGET_GROUP_ID = os.environ.get('TARGET_GROUP_ID')

print(f"Bot initialized with target group: {TARGET_GROUP_ID}")

# Rate limiting settings
MAX_MESSAGES = 5    
TIME_WINDOW = 60    
user_messages = defaultdict(list)  

def check_rate_limit(user_id: int) -> bool:
    current_time = datetime.now()
    user_messages[user_id] = [
        timestamp for timestamp in user_messages[user_id]
        if current_time - timestamp < timedelta(minutes=TIME_WINDOW)
    ]
    if len(user_messages[user_id]) >= MAX_MESSAGES:
        return False
    user_messages[user_id].append(current_time)
    return True

async def initialize_bot():
    bot = Bot(token=BOT_TOKEN)
    await bot.initialize()
    return bot

async def handle_update(update: Update):
    bot = await initialize_bot()
    
    if not update.message:
        return
        
    if update.message.text:
        if update.message.text.startswith('/start'):
            await bot.send_message(
                chat_id=update.message.chat.id,
                text="Hola! Envia'm qualsevol missatge i el publicaré de manera anònima al grup. "
                     "La teva identitat es mantindrà privada.\n\n"
                     f"Límit: {MAX_MESSAGES} missatges cada hora."
            )
            return
        elif update.message.text.startswith('/codi'):
            await bot.send_message(
                chat_id=update.message.chat.id,
                text="Pots trobar el codi font del bot aquí:\n"
                     "https://github.com/PBartrina/la-covardia-bot"
            )
            return

    if update.message.chat.type != 'private':
        return
    
    try:
        print(f"Processing message from user")
        
        user_id = update.message.from_user.id
        if not check_rate_limit(user_id):
            remaining_minutes = TIME_WINDOW - int((datetime.now() - user_messages[user_id][0]).total_seconds() / 60)
            time_msg = f"{remaining_minutes // 60} hora" if remaining_minutes >= 60 else f"{remaining_minutes} minuts"
            
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Has superat el límit de {MAX_MESSAGES} missatges per hora. "
                     f"Si us plau, espera {time_msg} més."
            )
            return

        try:
            bot_member = await bot.get_chat_member(chat_id=TARGET_GROUP_ID, user_id=bot.id)
            print(f"Bot permissions in group: {bot_member.to_dict()}")
        except Exception as e:
            print(f"Error checking bot permissions: {str(e)}")
            raise

        if update.message.text:
            print(f"Attempting to send text message to group {TARGET_GROUP_ID}")
            # Make text bold using Markdown
            bold_text = f"*{update.message.text}*"
            sent_message = await bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=bold_text,
                parse_mode='Markdown'  # Enable Markdown parsing
            )
            print(f"Message sent successfully with ID: {sent_message.message_id}")
        elif update.message.photo:
            print(f"Attempting to send photo to group {TARGET_GROUP_ID}")
            photo = update.message.photo[-1]
            # Make caption bold if it exists
            caption = f"*{update.message.caption}*" if update.message.caption else None
            sent_message = await bot.send_photo(
                chat_id=TARGET_GROUP_ID,
                photo=photo.file_id,
                caption=caption,
                parse_mode='Markdown' if caption else None
            )
            print(f"Photo sent successfully")
        elif update.message.document:
            print(f"Attempting to send document to group {TARGET_GROUP_ID}")
            # Make caption bold if it exists
            caption = f"*{update.message.caption}*" if update.message.caption else None
            sent_message = await bot.send_document(
                chat_id=TARGET_GROUP_ID,
                document=update.message.document.file_id,
                caption=caption,
                parse_mode='Markdown' if caption else None
            )
            print(f"Document sent successfully with ID: {sent_message.message_id}")
        
        messages_left = MAX_MESSAGES - len(user_messages[user_id])
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"El teu missatge s'ha publicat anònimament! ✅\n"
                 f"Et queden {messages_left} missatges en aquesta hora."
        )
        
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        error_details = f"Error type: {type(e).__name__}, Message: {str(e)}"
        print(error_details)
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"Ho sento, hi ha hagut un error en publicar el teu missatge. Si us plau, torna-ho a provar."
        )
    finally:
        await bot.shutdown()

@functions_framework.http
def telegram_webhook(request):
    if request.method != "POST":
        return "OK"

    try:
        update = Update.de_json(request.get_json(), None)
        asyncio.run(handle_update(update))
        return "OK"
    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        return str(e), 500 