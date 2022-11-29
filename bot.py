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
    update.message.reply_text(f"Здравствуй, {first_name}!")
    update.message.reply_text('Доступные команды: \n/start\n /planet Название планеты (например Mars)\n /wordcount\n /next_full_moon')

# Определение в каком созвездии находится планета Солнечной системы
def constellation(update, context):
    logger.debug("Вызван /planet")
    # потом добавить перечень всех объектов солнечной системы
    # all_solar_bodies = [name for _0, _1, name in ephem._libastro.builtin_planets()]
    date = datetime.datetime.now()
    user_text = update.message.text
    if user_text[8:] == '':
        raise ValueError(update.message.reply_text('Вы не ввели планету!'))
    user_text = user_text.split()
    planet = user_text[1]

    planet_func = getattr(ephem, planet, None)
    if not planet_func:
        return update.message.reply_text(f'Такой планеты или спутника - {planet} нет в Солнечной системе!')
    const = ephem.constellation(planet_func(date))[1]
    update.message.reply_text('{planet} сейчас находится в создвездии {const}'.format(planet = planet, const = const))



# Счётчик слов в предложении
def wordcount(update, context):
    logger.debug("Вызван /wordcount")
    user_text = update.message.text.strip()
    if user_text[11:] == '':
        raise ValueError(update.message.reply_text('Вы ничего не ввели!'))
    user_text = user_text[11:].split()
    update.message.reply_text(f'В предложении {len(user_text)} слов')

# Ближайшее полнолуние
def next_full_moon(update, context):
    logger.debug("Вызван /next_full_moon")
    date = datetime.datetime.now()
    nfm_date = ephem.next_full_moon(date)
    update.message.reply_text(f'Следующее полнолуние {nfm_date}')

def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", constellation))
    dp.add_handler(CommandHandler("wordcount", wordcount))
    dp.add_handler(CommandHandler("next_full_moon", next_full_moon))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logger.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
