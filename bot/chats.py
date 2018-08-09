from decorators import only_admin
from database import db


@only_admin
def connect(bot, update):
    chat_id = update.message.chat.id
    if db.chats.find_one({"chat": chat_id}) is None:
        db.chats.insert_one({"chat": chat_id})
        update.message.reply_text("\u2705 Chat added to subscriptions list")
    else:
        update.message.reply_text("\u2757\ufe0f This chat is already in subscriptions list")


@only_admin
def disconnect(bot, update):
    chat_id = update.message.chat.id
    if db.chats.find_one({"chat": chat_id}) is None:
        update.message.reply_text("\u2757\ufe0f This chat is not in subscriptions list")
    else:
        db.chats.delete_one({"chat": chat_id})
        update.message.reply_text("\u2705 Chat removed from subscriptions list")

