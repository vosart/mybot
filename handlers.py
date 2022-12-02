import csv
import datetime
from emoji import emojize
import ephem
import logging
from random import choice, randint, shuffle
import settings


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_smile(user_data):
    if 'emoji' not in user_data:
        smile = choice(settings.USER_EMOJI)
        return emojize(smile, language='alias')
    return user_data['emoji']

def talk_to_me(update, context):
    user_text = update.message.text
    context.user_data['emoji'] = get_smile(context.user_data)
    print(user_text)
    update.message.reply_text(f'user_text {context.user_data["emoji"]}')

def greet_user(update, context):
    context.user_data['emoji'] = get_smile(context.user_data)
    logger.debug("Вызван /start")
    first_name = update.message['chat']['first_name']
    update.message.reply_text(f'Здравствуй, {first_name}! {context.user_data["emoji"]}')
    update.message.reply_text('Доступные команды: \n/start\n /planet\n /wordcount\n /next_full_moon\n /guess_number\n /city_game')



# Определение в каком созвездии находится небесное тело
def constellation(update, context):
    logger.debug("Вызван /planet")
    print(context.args)
    all_sol_bodies = [name for _0, _1, name in ephem._libastro.builtin_planets()]

    user_text = context.args[0]

    if user_text == '':
        raise ValueError(update.message.reply_text('Вы не ввели планету! Чтобы узнать доступные тела, введите /planet ?'))
    elif user_text == '?':
        update.message.reply_text('Список доступных тел: \n')
        for pl in all_sol_bodies[:10]:
            update.message.reply_text(pl)
    else:
        date = datetime.datetime.now()
        planet = user_text
        planet_func = getattr(ephem, planet, None)
        if not planet_func:
            return update.message.reply_text(f'Такой планеты или спутника - {planet} нет в Солнечной системе!')
        const = ephem.constellation(planet_func(date))[1]
        update.message.reply_text('{planet} сейчас находится в создвездии {const}'.format(planet = planet, const = const))


# Счётчик слов в предложении
def wordcount(update, context):
    logger.debug("Вызван /wordcount")
    print(context.args)
    #user_text = update.message.text.strip()
    user_text = context.args[0]
    if user_text == '':
        raise ValueError(update.message.reply_text('Вы ничего не ввели!'))
    user_text_len = len(user_text)
    update.message.reply_text('В предложении {length} слов'.format(length = user_text_len))


# Ближайшее полнолуние
def next_full_moon(update, context):
    logger.debug("Вызван /next_full_moon")
    date = datetime.datetime.now()
    nfm_date = ephem.next_full_moon(date)
    update.message.reply_text(f'Следующее полнолуние {nfm_date}')


def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)
    if user_number > bot_number:
        message = f'Ваше число {user_number}, моё {bot_number}. Вы выиграли!'
    elif user_number == bot_number:
        message = f'Ваше число {user_number}, моё {bot_number}. Ничья!'
    else:
        message = f'Ваше число {user_number}, моё {bot_number}. Вы проиграли!'
    return message


def guess_number(update, context):
    print(context.args)
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_numbers(user_number)
        except (ValueError, TypeError):
            message = 'Введите целое число'
    else:
        message = 'Введите целое число'
    update.message.reply_text(message)


# Игра в города

def create_game_dict():
    list_of_cities = {}
    with open('city.csv', 'r', encoding='cp1251') as f:
        field = ["city_id", "country_id", "region_id", "name"]
        reader = csv.DictReader(f, field, delimiter=';')
        for row in reader:
            city = row['name']
            list_of_cities[city] = last_litera(city)
        return list_of_cities


def last_litera(city):
    stop_liters = ['ь', 'ъ', 'ы']
    if city[-1] not in stop_liters:
        return city[-1]
    else:
        return city[-2]


def next_city(list_city, user_city):
    if user_city not in list_city.keys():
        return 'Про такой город я не знаю...'    
    for city in list_city.keys():
        if city.lower()[0] == last_litera(user_city):
            return city

# добавление в context.user_data городов, которые называли и добавить на них проверку


def city_game(update, context):
    logger.debug("Вызван /city_game")
    list_city = create_game_dict()
    past_cities = []
    print('Города, которые уже называли: ', past_cities)
    #stop_game_words = ['stop', 'стоп', 'хватит']
    if context.args:
        user_city = context.args[0]
        if user_city not in past_cities:
            past_cities.append(user_city)
            context.user_data['cities'] = past_cities 
            print('context содержит - ', context.user_data['cities'])
            update.message.reply_text(f'Вы: {user_city}\n')
            bot_city = next_city(list_city, user_city)
            past_cities.append(bot_city)
            context.user_data['cities'].append(bot_city)
            update.message.reply_text(f'Бот: {bot_city}\n')
        else:
            update.message.reply_text(f'Такой город уже называли')
    else:
        update.message.reply_text('Вы ничего не ввели!')


