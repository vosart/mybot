import logging

from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

import settings
from anketa import (
    anketa_comment,
    anketa_name,
    anketa_rating,
    anketa_skip,
    anketa_start,
    anketa_wtf,
)
from handlers import *  # noqa: WPS347, F403
from menu import cmnd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    mybot.bot.set_my_commands(cmnd)

    anketa = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(/fill_anketa)$'), anketa_start),
        ],
        states={
            'name': [MessageHandler(Filters.text, anketa_name)],
            'rating': [MessageHandler(Filters.regex('^(1|2|3|4|5)$'), anketa_rating)],
            'comment': [
                CommandHandler('skip', anketa_skip),
                MessageHandler(Filters.text, anketa_comment),
            ],
        },
        fallbacks=[
            MessageHandler(Filters.all, anketa_wtf),
        ],
    )

    dp = mybot.dispatcher
    dp.add_handler(anketa)
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', constellation))
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(CommandHandler('city_game', city_game))
    dp.add_handler(CommandHandler('guess', guess_number))
    dp.add_handler(MessageHandler(Filters.photo, check_user_photo))
    dp.add_handler(MessageHandler(Filters.regex('^(Следующее полнолуние)$'), next_full_moon))
    dp.add_handler(MessageHandler(Filters.location, user_coordinates))

    logger.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
