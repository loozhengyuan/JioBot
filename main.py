import logging
import os
import argparse

import boto3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, PicklePersistence

from jiobot.handlers import commands, fallback
from jiobot.handlers.conversation import newevent

TELEGRAM_BOT_API_TOKEN = os.environ["TELEGRAM_BOT_API_TOKEN"]
INSTANCE_ID = os.environ["INSTANCE_ID"]


if __name__ == "__main__":
    # Initialise logging module
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )
    logging.info(f"Instance ID: {INSTANCE_ID}")

    # Define parser
    parser = argparse.ArgumentParser(description='JioBot Telegram Bot')

    # Add optional argument
    parser.add_argument("--first-run", action="store_true", help="Initialise files for first run")
    parser.add_argument("--ignore-local-data", action="store_true", help="Ignores local data file even if it exists")

    # Parse args
    args = parser.parse_args()
    logging.debug(f"Parsed arguments: {args}")

    # Create AWS S3 resource object
    s3 = boto3.resource('s3')

    # Set name of persistence data file
    persistence_file = "data/persistence.pickle"

    # Removes local copy of persistence file if desired
    if args.ignore_local_data:
        logging.warning(f"Local persistence file will be delete (if it even exists) since --ignore-local-data={args.ignore_local_data}")

        # Remove file
        logging.info(f"Checking for existence of {persistence_file}")
        if os.path.isfile(persistence_file):
            logging.info(f"File {persistence_file} was found!")
            os.remove(persistence_file)
            logging.debug(f"Deleted {persistence_file}")

    # Check if persistence file exists
    if not os.path.isfile(persistence_file):
        logging.error(f"File {persistence_file} was not found!")

        # Warn that new file will be created
        if args.first_run:
            logging.warning(f"File {persistence_file} will be newly created since --first-run={args.first_run}")

        # Get file from AWS S3 if not first time
        else:
            s3.meta.client.download_file(INSTANCE_ID, persistence_file, persistence_file)
            logging.debug(f"File {persistence_file} was successfully downloaded!")

    # Initialise persistence object
    pp = PicklePersistence(filename=persistence_file)

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

    # Backup latest file to AWS
    logging.info(f"Uploading {persistence_file} to AWS S3.")
    s3.meta.client.upload_file(persistence_file, INSTANCE_ID, persistence_file)
    logging.debug(f"File {persistence_file} was successfully uploaded!")
