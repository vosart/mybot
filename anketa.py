from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler


def anketa_start(update, context):
    update.message.reply_text(
        'Hi! What is your name?',
        reply_markup=ReplyKeyboardRemove(),
    )
    return 'name'


def anketa_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text('Enter correct first and second name')
        return 'name'
    context.user_data['anketa'] = {'name': user_name}
    reply_keyboard = [['1', '2', '3', '4', '5']]
    update.message.reply_text(
        'Please rate our bot from 1 to 5',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return 'rating'


def anketa_rating(update, context):
    context.user_data['anketa']['rating'] = int(update.message.text)
    update.message.reply_text('Enter comment or press /skip')
    return 'comment'


def anketa_comment(update, context):
    anketa = context.user_data['anketa']
    anketa['comment'] = update.message.text
    user_text = format_anketa(anketa)
    update.message.reply_text(user_text, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def anketa_skip(update, context):
    anketa = context.user_data['anketa']
    user_text = format_anketa(anketa)
    update.message.reply_text(user_text, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def format_anketa(anketa):
    user_text = f"""<b>Name:</b>: {anketa['name']}
<b>Rating</b>: {anketa['rating']}
"""
    if 'comment' in anketa:
        user_text += f"\n<b>Comment</b>: {anketa['comment']}"
    return user_text


def anketa_wtf(update, _):
    update.message.reply_text("I don't understand you...")
