import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, PicklePersistence

from jiobot.handlers import commands, fallback
from jiobot.handlers.conversation import newevent

TELEGRAM_BOT_API_TOKEN = os.environ["TELEGRAM_BOT_API_TOKEN"]


if __name__ == "__main__":
    # Initialise logging module
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )

    # Initialise persistence object
    pp = PicklePersistence(filename='data/persistence.pickle')

    # Initialise updater and dispatcher
    up = Updater(token=TELEGRAM_BOT_API_TOKEN, persistence=pp, use_context=True)
    dp = up.dispatcher

    # Command Handlers
    dp.add_handler(CommandHandler('start', commands.start))
    dp.add_handler(CommandHandler('help', commands.help))
    dp.add_handler(CommandHandler('about', commands.about))

    # Conversation Handler - /newevent command
    dp.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler('newevent', newevent.entry),
            ],
            states={
                newevent.STATES.GET_EVENT_NAME: [
                    MessageHandler(Filters.text, newevent.handle_event_name),
                ],
                newevent.STATES.GET_RSVP: [
                    CallbackQueryHandler(newevent.handle_rsvp),
                    CommandHandler('endevent', newevent.end_event),
                ],
            },
            fallbacks=[
                CommandHandler('abort', newevent.abort),
                MessageHandler(Filters.command, newevent.fallback),
                MessageHandler(Filters.text, newevent.fallback),
            ],
            persistent=True,
            name="conversation_newevent",
            per_user=False,
        )
    )

    # Unknown Handlers
    dp.add_handler(MessageHandler(Filters.command, fallback.unknown))
    dp.add_handler(MessageHandler(Filters.text, fallback.unknown))

    # Start the Bot
    up.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    up.idle()
