import random

from telegram import ChatAction
from telegram.ext import run_async

from jiobot.decorators import send_typing_action

@run_async
@send_typing_action
def unknown(update, context):
    """Handles fallback for all unknown input"""

    # List of phrases/sentences with the same meaning
    texts = [
        "Eh wah, I don't recognise this. Refer to /help for a list of commands that I listen to.",
        "Paiseh, I don't know what you saying. Refer to /help for a list of commands that I listen to.",
    ]

    # Sends a text with error message
    context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(texts))
