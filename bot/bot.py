#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler

from config import *

# Bot functions
import chats
import clients
import info
import testing

import logging

logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
)
logger = logging.getLogger(__name__)


def error(bot, update, info):
    logger.warning('Update "%s" caused error "%s"', update, info)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", info.start))
    dp.add_handler(CommandHandler("register", clients.register, pass_args=True))
    dp.add_handler(CommandHandler("check", testing.check, pass_args=True))
    dp.add_handler(CommandHandler("connect", chats.connect))
    dp.add_handler(CommandHandler("disconnect", chats.disconnect))
    dp.add_handler(CommandHandler("status", info.status))
    dp.add_handler(CommandHandler("revoke", clients.revoke, pass_args=True))
    dp.add_handler(CommandHandler("generate", clients.generate, pass_args=True))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

