from config import *

def only_admin(func):
    def inner(bot, update, *args, **kwargs):
        if not update.message:
            return
        if update.message.from_user.id not in ADMINS:
            return
        return func(bot, update, *args, **kwargs)
    return inner


def only_pm(func):
    def inner(bot, update, *args, **kwargs):
        if not update.message:
            return
        if update.message.chat.id != update.message.from_user.id:
            return
        return func(bot, update, *args, **kwargs)
    return inner

