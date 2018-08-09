from decorators import only_pm
from database import db, DESC
from datetime import datetime


def status(bot, update):
    check_info = db.checks.find_one({}, sort=[("ts", DESC)])
    
    message = "Last checked at **{}** UTC\n\n".format(datetime.fromtimestamp(check_info["ts"]).strftime('%H:%M:%S'))

    for client in check_info["result"]:
        if check_info["result"][client] == "ok":
            message += "\u2705"
        elif check_info["result"][client] == "fail":
            message += "\u274c"
        else:
            message += "\ud83d\udc80"

        message += " {cn}\n".format(cn=client)

    message += "\n\u2705 OK · \u274c proxy failed · \ud83d\udc80 client down"
    update.message.reply_markdown(message)



@only_pm
def start(bot, update):
    update.message.reply_text('''Hi! It's RKN Monitor project — we analyze how Russian authorities try blocking Telegram in Russia.

Source code: https://github.com/nsychev/rknmon
To join, send @nsychev your city and Internet provider name.''', disable_web_page_preview=True)

