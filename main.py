import os
import functions_framework
from telegram import Update, Bot
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import telegram

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TARGET_GROUP_ID = os.environ.get('TARGET_GROUP_ID')

print(f"Bot initialized with target group: {TARGET_GROUP_ID}")

# Rate limiting settings
MAX_MESSAGES = 5    
TIME_WINDOW = 60    
user_messages = defaultdict(list)  

# Add at the top with other global variables
TOTAL_MESSAGES = 0
TOTAL_PHOTOS = 0
TOTAL_DOCUMENTS = 0

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
    global TOTAL_MESSAGES
    global TOTAL_PHOTOS
    global TOTAL_DOCUMENTS
    
    bot = await initialize_bot()
    
    if not update.message:
        return
        
    if update.message.text:
        if update.message.text.startswith('/start'):
            await bot.send_message(
                chat_id=update.message.chat.id,
                text="Hola! Envia'm qualsevol missatge i el publicaré de manera anònima al grup. "
                     "La teva identitat es mantindrà privada.\n\n"
                     f"Límit: {MAX_MESSAGES} missatges cada hora.\n\n"
                     "Comandes disponibles:\n"
                     "/ajuda - Mostra aquest missatge\n"
                     "/codi - Enllaç al codi font\n"
                     "/quota - Consulta els missatges que et queden\n"
                     "/stats - Mostra estadístiques d'ús"
            )
            return
        elif update.message.text.startswith('/ajuda'):
            await bot.send_message(
                chat_id=update.message.chat.id,
                text="Hola! Envia'm qualsevol missatge i el publicaré de manera anònima al grup. "
                     "La teva identitat es mantindrà privada.\n\n"
                     f"Límit: {MAX_MESSAGES} missatges cada hora.\n\n"
                     "Comandes disponibles:\n"
                     "/ajuda - Mostra aquest missatge\n"
                     "/codi - Enllaç al codi font\n"
                     "/quota - Consulta els missatges que et queden\n"
                     "/stats - Mostra estadístiques d'ús"
            )
            return
        elif update.message.text.startswith('/quota'):
            messages_left = MAX_MESSAGES - len(user_messages[update.message.from_user.id])
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Et queden {messages_left} missatges en aquesta hora."
            )
            return
        elif update.message.text.startswith('/codi'):
            await bot.send_message(
                chat_id=update.message.chat.id,
                text="Pots trobar el codi font del bot aquí:\n"
                     "https://github.com/PBartrina/la-covardia-bot"
            )
            return
        elif update.message.text.startswith('/stats'):
            await bot.send_message(
                chat_id=update.message.chat.id,
                text="📊 Estadístiques des de l'última actualització del bot:\n\n"
                     f"• Missatges de text: {TOTAL_MESSAGES}\n"
                     f"• Fotos: {TOTAL_PHOTOS}\n"
                     f"• Documents: {TOTAL_DOCUMENTS}\n"
                     f"• Total: {TOTAL_MESSAGES + TOTAL_PHOTOS + TOTAL_DOCUMENTS}\n\n"
                     "⚠️ Aquestes estadístiques es reinicien quan s'actualitza el bot."
            )
            return

    if update.message.chat.type != 'private':
        return
    
    try:
        print("Message received")
        
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
            print("Message forwarded to group")
            # Clean potentially problematic characters from messages before sending
            def clean_message(text):
                # Remove any Markdown characters that could break formatting
                return text.replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')

            # Then in the send message part:
            bold_text = f"*{clean_message(update.message.text)}*"
            sent_message = await bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=bold_text,
                parse_mode='Markdown'  # Enable Markdown parsing
            )
            print(f"Message sent successfully with ID: {sent_message.message_id}")
            TOTAL_MESSAGES += 1
        elif update.message.photo:
            print("Message forwarded to group")
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
            TOTAL_PHOTOS += 1
        elif update.message.document:
            print("Message forwarded to group")
            # Make caption bold if it exists
            caption = f"*{update.message.caption}*" if update.message.caption else None
            sent_message = await bot.send_document(
                chat_id=TARGET_GROUP_ID,
                document=update.message.document.file_id,
                caption=caption,
                parse_mode='Markdown' if caption else None
            )
            print(f"Document sent successfully with ID: {sent_message.message_id}")
            TOTAL_DOCUMENTS += 1
        
        messages_left = MAX_MESSAGES - len(user_messages[user_id])
        await bot.send_message(
            chat_id=update.message.chat.id,
            text=f"El teu missatge s'ha publicat anònimament! ✅\n"
                 f"Et queden {messages_left} missatges en aquesta hora."
        )
        
    except telegram.error.Unauthorized:
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="No tinc permís per enviar missatges al grup. Contacta amb l'administrador."
        )
    except telegram.error.TimedOut:
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="El servidor triga massa a respondre. Torna-ho a provar d'aquí uns minuts."
        )
    except Exception as e:
        await bot.send_message(
            chat_id=update.message.chat.id,
            text="Hi ha hagut un error inesperat. Torna-ho a provar més tard."
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