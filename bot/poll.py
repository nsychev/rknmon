from time import time, sleep
from telegram import Bot
from config import *
from database import db, DESC
import traceback
import network

bot = Bot(TOKEN)


def notify(message):
    for chat in db.chats.find({}):
        bot.send_message(chat_id=chat["chat"], text=message, parse_mode="Markdown")


def check_all():
    EMOJI = {
        "ok": "\u2705",
        "fail": "\u274c",
        "down": "\ud83d\udc80"
    }

    INFO = {
        "ok": "is OK",
        "fail": "can't reach {host}".format(host=HOST),
        "down": "is down"
    }

    last_check = db.checks.find_one({}, sort=[("ts", DESC)])
    
    if last_check is None:
        last_result = {}
        last_ip = ""
    else:
        last_result = last_check["result"]
        last_ip = last_check["ip"]
    
    ip = network.resolve(HOST)

    if ip != last_ip:
        notify("\ud83d\udd01 *{host}* has new IP address: *{ip}*".format(host=HOST, ip=ip))

    result = {}

    for client in db.clients.find({}):
        if not client["ip"]:
            verdict = "down"
        elif network.connect(ip, 1080, client["ip"]):
            verdict = "ok"
        elif network.connect(network.resolve(DUMMY_HOST), 80, client["ip"]):
            verdict = "fail"
        else:
            verdict = "down"

        result[client["cn"]] = verdict

        if verdict != last_result.get(client["cn"], "down"):
            bot.send_message(
                    chat_id=client["owner"],
                    text="{em} Your client *{cn}* {state}".format(em=EMOJI[verdict], cn=client["cn"], state=INFO[verdict]),
                    parse_mode="Markdown"
            )
            
        if verdict == "fail" and last_result.get(client["cn"], "down") == "ok":
            notify("\u274c Failed to connect via *{cn}* to *{host}* ({ip})".format(cn=client["cn"], host=HOST, ip=ip))
        if verdict == "ok" and last_result.get(client["cn"], "down") == "fail":
            notify("\u2705 Client *{cn}* restored connection to *{host}* ({ip})".format(cn=client["cn"], host=HOST, ip=ip))
    
    db.checks.insert_one({
        "ts": time(),
        "ip": ip,
        "result": result
    })

    return result, ip


def main():
    while True:
        try:
            result, ip = check_all()
        except:
            traceback.print_exc()
            continue
        
        st = {"ok": 0, "fail": 0, "down": 0}
        for client in result:
            st[result[client]] += 1

        print("Resolve:", ip, "-", st["ok"], "succeeded,", st["fail"], "failed,", st["down"], "down", flush=True)

        sleep(30)

if __name__ == "__main__":
    main()

