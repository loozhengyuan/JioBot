import textwrap
import random

from telegram import ParseMode, ChatAction
from telegram.ext import run_async

from jiobot.decorators import send_typing_action

MENU = """
I'm @JioBot and I manage events for you. Use any of these commands to talk to me.

*General Commands*
/help - Displays this menu of commands
/about - More information about this bot

*Event Commands*
/newevent - Creates a new event

P.S. I'm new so I can only handle one event at a time :(
"""


@run_async
@send_typing_action
def start(update, context):
    """Handles the entry point for the chatbot"""

    # Get user information
    user_id = update.message.from_user.id
    user_fullname = update.message.from_user.full_name

    # Greets user
    texts = [
        f'Hey <a href="tg://user?id={user_id}">{user_fullname}</a>!',
        f'Hello <a href="tg://user?id={user_id}">{user_fullname}</a>!',
    ]
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=random.choice(texts),
        parse_mode=ParseMode.HTML,
    )

    # Sends a text containing a list of applicable commands
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=textwrap.dedent(MENU),
        parse_mode=ParseMode.MARKDOWN
    )


@run_async
@send_typing_action
def help(update, context):
    """Displays menu for the user"""

    # Sends a text containing a list of applicable commands
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=textwrap.dedent(MENU),
        parse_mode=ParseMode.MARKDOWN
    )


@run_async
@send_typing_action
def about(update, context):
    """Displays about information for the user"""

    # Sends a text containing a list of applicable commands
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm @JioBot and I help manage events. I'm still fairly new, and learning every day. I can only listen to commands because my creator doesn't really have time to teach me. Please be kind with me, and feel free to visit [my home](https://github.com/loozhengyuan/jiobot) if you have any ideas how you can make me better!",
        parse_mode=ParseMode.MARKDOWN
    )
