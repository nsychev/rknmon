from database import db
import network
from config import *


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

    ping_result = network.ping(client["ip"])
    if ping_result:
        message += "\u2705 Ping OK\n"
    else:
        message += "\u274c Ping failed\n"

    for host, port in [(DUMMY_HOST, 80), (HOST, 1080)]:
        ip = network.resolve(host)
        connect_result = network.connect(ip, port, client["ip"])
        if connect_result:
            message += "\u2705 Connect to {host} ({ip}) OK\n".format(host=host, ip=ip)
        else:
            message += "\u274c Connect to {host} ({ip}) failed\n".format(host=host, ip=ip)

    update.message.reply_html(message)


