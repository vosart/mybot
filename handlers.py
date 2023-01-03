import csv
import datetime
import logging
import os
from random import choice

import ephem

from utils import has_object_on_image, play_random_numbers

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


def greet_user(update, context):
    logger.debug('Вызван /start')
    first_name = update.message['chat']['first_name']
    update.message.reply_text(f'Здравствуй, {first_name}!')


def user_coordinates(update, _):
    return update.message.location


# Определение в каком созвездии находится небесное тело
def constellation(update, context):
    logger.debug('Вызван /planet')
    all_sol_bodies = [name for _, _, name in ephem._libastro.builtin_planets()]  # noqa: WPS437

    if not context.args:
        update.message.reply_text('Чтобы узнать доступные тела, введите /planet ?')
        return

    user_text = context.args[0]

    if user_text == '?':
        update.message.reply_text('Список доступных тел: \n')
        for pl in all_sol_bodies[:10]:
            update.message.reply_text(pl)
        return

    date = datetime.datetime.now()
    planet = user_text
    planet_func = getattr(ephem, planet, None)
    if not planet_func:
        return update.message.reply_text(f'{planet} нет в Солнечной системе!')
    const = ephem.constellation(planet_func(date))[1]
    update.message.reply_text(f'{planet} сейчас находится в создвездии {const}')


# Счётчик слов в предложении
def wordcount(update, context):
    logger.debug('Вызван /wordcount')

    if not context.args:
        update.message.reply_text('Вы ничего не ввели')
        return
    user_text = context.args

    user_text_len = len(user_text)
    update.message.reply_text('В предложении {length} слов'.format(length=user_text_len))


# Ближайшее полнолуние
def next_full_moon(update, _):
    logger.debug('Вызван /next_full_moon')
    date = datetime.datetime.now()
    nfm_date = ephem.next_full_moon(date)
    update.message.reply_text(f'Следующее полнолуние {nfm_date}')


# Игра в числа
def guess_number(update, context):
    if not context.args:
        update.message.reply_text('Вы ничего не ввели')
        return

    try:
        user_number = int(context.args[0])
        message = play_random_numbers(user_number)
    except (ValueError, TypeError):
        message = 'Введите целое число'

    update.message.reply_text(message)


# Игра в города

def last_litera(city) -> str:
    stop_liters = {'ь', 'ъ', 'ы'}
    if city[-2] not in stop_liters:
        return city[-2]
    return city[-2]


def load_cities() -> dict[str, str]:
    cities = {}
    with open('cities.csv', 'r', encoding='cp1251') as file:
        field = ['city_id', 'country_id', 'region_id', 'name']
        reader = csv.DictReader(file, field, delimiter=';')
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
    return choice(cities_to_choose)  # noqa: S311


def get_cities_in_game(past_cities: list[str]) -> dict[str, str]:
    cities = {}
    for city, litera in all_cities.items():
        if city in past_cities:
            continue
        cities[city] = litera
    return cities


def city_game(update, context):
    logger.debug('Вызван /city_game')
    past_cities = context.user_data.get('cities') or []
    cities_in_game = get_cities_in_game(past_cities)

    if not context.args:
        update.message.reply_text('Вы ничего не ввели!')
        return

    user_city = context.args[0]

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


def check_user_photo(update, context):
    update.message.reply_text('Обработка фото')
    os.makedirs('downloads', exist_ok=True)
    get_file = update.message.photo[-1].file_id
    photo_file = context.bot.getFile(get_file)
    file_name = os.path.join('downloads', f'{get_file}.jpg')
    photo_file.download(file_name)
    update.message.reply_text('Файл сохранен')
    if has_object_on_image(file_name, 'cat'):
        update.message.reply_text('Обнаружен котик, сохраняю к себе')
        new_file_name = os.path.join('images', f'cat_{photo_file.file_id}.jpg')
        os.rename(file_name, new_file_name)
    else:
        os.remove(file_name)
        update.message.reply_text('Котик не обнаружен!')
