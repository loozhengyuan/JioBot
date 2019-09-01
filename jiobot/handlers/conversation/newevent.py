import logging

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.chat import Chat
from telegram.ext import ConversationHandler

from jiobot.decorators import send_typing_action

EVENT_STATUS = "<b>{event_name}</b>\n{attendees}{nonattendees}"

RSVP_OPEN = "\nYou may /endevent to stop RSVPs."


class STATES:
    GET_EVENT_NAME = "GET_EVENT_NAME"
    GET_RSVP = "GET_RSVP"


class RSVP:
    YES = "YES"
    NO = "NO"


@send_typing_action
def entry(update, context):
    """Handles the entry point for the chatbot"""

    # Deletes chat_data if it currently exists
    context.chat_data['newevent'] = {}
    context.chat_data['newevent']['rsvp'] = {}

    # Get user information
    user_id = update.message.from_user.id
    user_fullname = update.message.from_user.full_name

    # Sends a text reply
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Ok <a href="tg://user?id={user_id}">{user_fullname}</a>, tell me a short and sweet name for your event. (e.g. Supper later at 10pm)',
        parse_mode=ParseMode.HTML,
        reply_markup=ForceReply(selective=True),
    )

    return STATES.GET_EVENT_NAME


@send_typing_action
def handle_event_name(update, context):
    """Handles response for event name"""

    # Get event name
    event_name = update.message.text

    # Store event name in context
    try:
        context.chat_data['newevent']['event_name'] = event_name
    except KeyError:
        logging.error("Tried to access event name in persisted user data but was not found!", exc_info=True)
        return ConversationHandler.END

    # Create button keyboard
    buttons = [
        [
            InlineKeyboardButton(RSVP.YES, callback_data=RSVP.YES),
            InlineKeyboardButton(RSVP.NO, callback_data=RSVP.NO),
        ],
    ]
    markup = InlineKeyboardMarkup(buttons)

    # List of phrases/sentences with the same meaning
    message = context.bot.send_message(
        chat_id=update.message.chat_id,
        text=EVENT_STATUS.format(
            event_name=event_name,
            attendees="",
            nonattendees="",
        ) + RSVP_OPEN,
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
    )
    context.chat_data['newevent']['message_id'] = message.message_id

    return STATES.GET_RSVP


def handle_rsvp(update, context):
    """Handles state for getting rsvp responses"""

    # Get RSVP choices
    # TODO: Implement __contains__ and check validity
    choice = update.callback_query.data
    logging.info(f"User @{update.callback_query.from_user.username} selected {choice}")
    if choice not in [RSVP.YES, RSVP.NO]:
        logging.info(f"User @{update.callback_query.from_user.username} did not choose YES or NO, terminating conversation.")
        return ConversationHandler.END

    # Retrieves user information
    user_handle = update.callback_query.from_user.username
    if not user_handle:
        # Get other information from user
        user_id = update.callback_query.from_user.id
        user_fullname = update.callback_query.from_user.full_name
        # Sends a text reply
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f'Sorry <a href="tg://user?id={user_id}">{user_fullname}</a>, please set your username first so I can register you',
            parse_mode=ParseMode.HTML,
        )

        # Answer callback
        context.bot.answer_callback_query(update.callback_query.id)
        return STATES.GET_RSVP

    # Add to context
    if context.chat_data['newevent']['rsvp'].get(user_handle) == choice:
        # Answer callback
        logging.info(f"User @{update.callback_query.from_user.username}'s previous choice was already {choice}")
        context.bot.answer_callback_query(update.callback_query.id)
        return STATES.GET_RSVP
    else:
        logging.info(f"Setting @{update.callback_query.from_user.username}'s choice to {choice}")
        context.chat_data['newevent']['rsvp'][user_handle] = choice

    # Generate attendee lists
    attendees = []
    nonattendees = []
    for user, rsvp in context.chat_data['newevent']['rsvp'].items():
        if rsvp == RSVP.YES:
            attendees.append(f"@{user}")
        elif rsvp == RSVP.NO:
            nonattendees.append(f"@{user}")

    # Create button keyboard
    buttons = [
        [
            InlineKeyboardButton(RSVP.YES, callback_data=RSVP.YES),
            InlineKeyboardButton(RSVP.NO, callback_data=RSVP.NO),
        ],
    ]
    markup = InlineKeyboardMarkup(buttons)

    # List of phrases/sentences with the same meaning
    event_name = context.chat_data['newevent']['event_name']
    if attendees:
        attendees = "\n<i>Attending:</i>\n" + "\n".join(attendees) + "\n"
    else:
        attendees = ""
    if nonattendees:
        nonattendees = "\n<i>Not Attending:</i>\n" + "\n".join(nonattendees) + "\n"
    else:
        nonattendees = ""
    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text=EVENT_STATUS.format(
            event_name=event_name,
            attendees=attendees,
            nonattendees=nonattendees,
        ) + RSVP_OPEN,
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
    )

    # Answer callback
    context.bot.answer_callback_query(update.callback_query.id)
    return STATES.GET_RSVP


@send_typing_action
def end_event(update, context):
    """Handles intent to stop accepting rsvp responses"""

    # Get message_id of event status
    chat_type = update.effective_chat.type
    if chat_type != Chat.PRIVATE:
        message_id = update.message.reply_to_message.message_id
    else:
        message_id = context.chat_data['newevent']['message_id']

    # Generate attendee lists
    attendees = []
    nonattendees = []
    for user, rsvp in context.chat_data['newevent']['rsvp'].items():
        if rsvp == RSVP.YES:
            attendees.append(f"@{user}")
        elif rsvp == RSVP.NO:
            nonattendees.append(f"@{user}")

    # List of phrases/sentences with the same meaning
    event_name = context.chat_data['newevent']['event_name']
    if attendees:
        attendees = "\n<i>Attending:</i>\n" + "\n".join(attendees) + "\n"
    else:
        attendees = ""
    if nonattendees:
        nonattendees = "\n<i>Not Attending:</i>\n" + "\n".join(nonattendees) + "\n"
    else:
        nonattendees = ""
    context.bot.edit_message_text(
        chat_id=update.message.chat_id,
        message_id=message_id,
        text=EVENT_STATUS.format(
            event_name=event_name,
            attendees=attendees,
            nonattendees=nonattendees,
        ),
        parse_mode=ParseMode.HTML,
    )

    # Sends a text reply
    message = "RSVP has closed!"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        reply_to_message_id=message_id,
        text=message,
    )

    # Deletes chat_data if it currently exists
    if context.chat_data.get("newevent"):
        del context.chat_data['newevent']

    return ConversationHandler.END


@send_typing_action
def event_currently_exists(update, context):
    """Handles if an event currently exists"""

    # Sends a text reply
    message = "Sorry, I can only manage one event at a time - at least for now. Of course, you may /abort the current event if you wish to do so."
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


@send_typing_action
def fallback(update, context):
    """Handles fallback for any conversation"""

    # Sends a text reply
    message = "I'm busy managing an event right now. If you have a running event right now, you may /endevent to stop receiving RSVPs or simply /abort the current event if you wish to do so."
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


@send_typing_action
def abort(update, context):
    """Handles exit for any conversation"""

    # Sends a text reply
    message = "Event aborted. You can create a /newevent or use /help to get a full list of commands."
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

    # Deletes chat_data if it currently exists
    if context.chat_data.get("newevent"):
        del context.chat_data['newevent']

    return ConversationHandler.END
