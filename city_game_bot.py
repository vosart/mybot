import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import settings
from handlers import *


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

CITY_GAME, LITERA = range(3)

def city_game(update, _):
    update.message.reply_text('Хотите поиграть в города? Тогда начинаем!\n Вы:')
    return CITY_GAME

def city_game_start(update, _):
    keyboard = [[InlineKeyboardButton("Stop", callback_data="stop_game")]]
    city = update.message.text
    last_litera = city[-1]
    update.message.reply_text(f'Мне на {last_litera.upper()}', reply_markup=InlineKeyboardMarkup(keyboard))

    print(city)

    update.message.reply_text('Мне на {last_litera}'.format(last_litera))
    return CITY_GAME

def stop(update, context):
    update.callback_query.message.edit_reply_markup(None)
    text = f'Спасибо за игру {update.callback_query.from_user.full_name}'
    update.callback_query.answer(text, show_alert = True)
    return ConversationHandler.END


def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    handler = ConversationHandler(
        entry_points=[CommandHandler('city_game', city_game)],
        states={
            CITY_GAME: [CommandHandler('stop', stop), MessageHandler(Filters.text, city_game_start), ],
        },
        fallbacks=[]
    )
    dp.add_handler(handler)
    dp.add_handler(CallbackQueryHandler(query))



    logger.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
