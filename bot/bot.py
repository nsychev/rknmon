#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import logging
from pymongo import MongoClient, DESCENDING as DESC
from config import *
import re
import os
from utils import *
from datetime import datetime

logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
)
logger = logging.getLogger(__name__)
db = MongoClient().db
cn_re = re.compile(r"^[a-z-]+$")


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


@only_pm
def register(bot, update, args):
    if len(args) != 1:
        update.message.reply_text("\u274c Usage: /register [common_name]")
        return

    common_name = args[0]

    if db.clients.find_one({"cn": common_name}) is not None:
        update.message.reply_text("\u274c This client is already registered")
        return

    if not cn_re.match(common_name):
        update.message.reply_text("\u274c CN is invalid")
        return
    
    if not os.path.exists("/root/conf/output/{cn}.ovpn".format(cn=common_name)):
        update.message.reply_text("\u274c Client config for this CN does not exist")
        return

    db.clients.insert_one({
        "cn": common_name,
        "owner": update.message.from_user.id,
        "ip": None
    })

    update.message.reply_html('''\u2705 Successfly registered as <b>{cn}</b>!

<b>Next steps:</b>
1. Install <a href="https://openvpn.net/index.php/download/community-downloads.html">OpenVPN</a>
– on Debian: <code>apt install -y openvpn</code>
2. Place file <b>{cn}.conf</b> into <b>/etc/openvpn</b>
3. Run OpenVPN client
– on Debian: <code>service openvpn restart</code>
4. Type /check {cn} to ensure that everything works as expected.

Also you can try blocking connections to {host} and checking again.

Questions? @nsychev'''.format(cn=common_name, host=HOST), disable_web_page_preview=True)
    update.message.reply_document(document=open("/root/conf/output/{cn}.ovpn".format(cn=common_name), "rb"), filename=common_name+".conf")


@only_pm
def check(bot, update, args):
    if len(args) != 1:
        update.message.reply_text("\u274c Usage: /check [common_name]")
        return

    common_name = args[0]

    client = db.clients.find_one({"cn": common_name})

    if client is None:
        update.message.reply_text("\u274c This client does not exist")
        return

    if update.message.from_user.id != client["owner"] and update.message.from_user.id not in ADMINS:
        update.message.reply_text("\u274c You don't have privileges to check this client")
        return
    
    if client["ip"] is None:
        update.message.reply_text("\u274c Client is not connected")
        return
    
    message = "Client <b>{cn}</b> ({ip})\n\n".format(cn=common_name, ip=client["ip"])

    ping_result = ping(client["ip"])
    if ping_result:
        message += "\u2705 Ping OK\n"
    else:
        message += "\u274c Ping failed\n"

    for host, port in [(DUMMY_HOST, 80), (HOST, 1080)]:
        ip = get_ip(host)
        connect_result = sock_connect(ip, port, client["ip"])
        if connect_result:
            message += "\u2705 Connect to {host} ({ip}) OK\n".format(host=host, ip=ip)
        else:
            message += "\u274c Connect to {host} ({ip}) failed\n".format(host=host, ip=ip)

    update.message.reply_html(message)


def status(bot, update):
    check_info = db.checks.find_one({}, sort=[("ts", DESC)])
    
    message = "Last checked at **{}** UTC\n\n".format(datetime.fromtimestamp(check_info["ts"]).strftime('%H:%M:%S'))

    for client in check_info["result"]:
        if check_info["result"][client] == "ok":
            message += "\u2705"
        elif check_info["result"][client] == "fail":
            message += "\u274c"
        else:
            message += "\u2757\ufe0f"

        message += " {cn}\n".format(cn=client)

    message += "\n\u2705 OK · \u274c **sox.ctf.su** failed · \u2757\ufe0f client down"
    update.message.reply_markdown(message)


@only_admin
def revoke(bot, update, args):
    if len(args) != 1:
        update.message.reply_text("usage: /revoke [common_name]")
        return
    
    db.clients.delete_one({"cn": args[0]})
    update.message.reply_text("\u2705 OK")


@only_pm
def start(bot, update):
    update.message.reply_text("Hi! If you want to join RKN Monitoring Project, send @nsychev your city and provider. He will provide a common name for your VPN client, then type /register common_name to continue.")


def error(bot, update, info):
    logger.warning('Update "%s" caused error "%s"', update, info)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("register", register, pass_args=True))
    dp.add_handler(CommandHandler("check", check, pass_args=True))
    dp.add_handler(CommandHandler("connect", connect))
    dp.add_handler(CommandHandler("disconnect", disconnect))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("revoke", revoke, pass_args=True))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

