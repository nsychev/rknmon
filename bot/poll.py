from utils import *
from pymongo import MongoClient, DESCENDING as DESC
from time import time, sleep
from telegram import Bot
from config import *
import traceback

db = MongoClient().db
bot = Bot(TOKEN)


def notify(message):
    for chat in db.chats.find({}):
        bot.send_message(chat_id=chat["chat"], text=message, parse_mode="Markdown")


def check_all():
    last_check_info = db.checks.find_one({}, sort=[("ts", DESC)])
    
    if last_check_info is None:
        last_check_result = {}
        last_check_resolve = ""
    else:
        last_check_result = last_check_info["result"]
        last_check_resolve = last_check_info["ip"]
    
    ip = get_ip(HOST)

    if ip != last_check_resolve:
        notify("\ud83d\udd01 *{host}* changed IP to *{ip}*".format(host=HOST, ip=ip))

    result = {}

    for client in db.clients.find({}):
        if not client["ip"]:
            result[client["cn"]] = "down"
        elif sock_connect(ip, 1080, client["ip"]):
            result[client["cn"]] = "ok"
        elif sock_connect(get_ip(DUMMY_HOST), 80, client["ip"]):
            result[client["cn"]] = "fail"
        else:
            result[client["cn"]] = "down"

        if result[client["cn"]] == "down" and last_check_result.get(client["cn"], "down") != "down":
            bot.send_message(chat_id=client["owner"], text="\u2757\ufe0f Your client *{cn}* has fallen down".format(cn=client["cn"]), parse_mode="Markdown")
        if result[client["cn"]] == "fail" and last_check_result.get(client["cn"], "ok") == "ok":
            notify("\u274c Failed to connect via *{cn}* to *{host}* ({ip})".format(cn=client["cn"], host=HOST, ip=ip))
    
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
