import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def talk_to_me(update, context):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text(user_text)

def greet_user(update, context):
    logger.debug("Вызван /start")
    first_name = update.message['chat']['first_name']
    last_name = update.message['chat']['last_name'] or ''
    update.message.reply_text(f"Здравствуй, {first_name} {last_name.strip()}!")   

def constellation(update, context):
    logger.debug("Вызван /planet")
    date = datetime.datetime.now()
    user_text = update.message.text.split()
    planet = user_text[1]
    func = getattr(ephem, planet)
    const = ephem.constellation(func(date))[1]
    update.message.reply_text(f'{planet} сейчас находится в создвездии {const}')


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", constellation))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    
    logger.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
