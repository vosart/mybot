import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

import settings
from handlers import *

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

CITY_GAME = 1

def last_litera(city) -> str:
    stop_liters = {'ь', 'ъ', 'ы'}
    if city[-1] not in stop_liters:
        return city[-1]
    else:
        return city[-2]


def load_cities() -> dict[str, str]:
    cities = {}
    with open('cities.csv', 'r', encoding='cp1251') as f:
        field = ["city_id", "country_id", "region_id", "name"]
        reader = csv.DictReader(f, field, delimiter=';')
        for row in reader:
            city_name = row['name']
            cities[city_name] = last_litera(city_name)
        return cities


all_cities = load_cities()


def next_city(cities_in_game: dict[str, str], user_city: str) -> str:
    cities_to_choose = []
    for city in cities_in_game.keys():
        if city.lower()[0] == all_cities[user_city]:
            cities_to_choose.append(city)
    return choice(cities_to_choose)


def get_cities_in_game(past_cities: list[str]) -> dict[str, str]:
    cities = {}
    for city, litera in all_cities.items():
        if city in past_cities:
            continue
        cities[city] = litera
    return cities


def city_game(update, context):
    logger.debug("Вызван /city_game")
    user_city = update.message.text
    past_cities = context.user_data.get('cities') or []
    cities_in_game = get_cities_in_game(past_cities)

    print('Города, которые уже называли: ', past_cities)
    #stop_game_words = ['stop', 'стоп', 'хватит']


    if not user_city:
        update.message.reply_text('Вы ничего не ввели!')
        return


    if user_city not in all_cities:
        update.message.reply_text('Про такой город я не знаю...')
        return

    if user_city in past_cities:
        update.message.reply_text('Такой город уже называли')
        return


    past_cities.append(user_city)
    bot_city = next_city(cities_in_game, user_city)
    past_cities.append(bot_city)
    context.user_data['cities'] = past_cities
    update.message.reply_text(f'Бот: {bot_city}\n')
    return CITY_GAME

def city_game_start(update, _):
    keyboard = ReplyKeyboardMarkup([["/stop"]], resize_keyboard=True)
    update.message.reply_text('Хотите поиграть в города? Тогда начинаем!\n', reply_markup=keyboard)
    return CITY_GAME

def stop(update, _):
    update.message.reply_text('Спасибо за игру!\n')
    return ConversationHandler.END


def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text, city_game_start)],
        states={
            CITY_GAME: [CommandHandler('stop', stop), MessageHandler(Filters.text, city_game)],
        },
        fallbacks=[]
    )
    dp.add_handler(handler)

    logger.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
