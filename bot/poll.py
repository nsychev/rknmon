from time import time, sleep
from telegram import Bot
from config import *
from database import db, DESC
import traceback
import network
from datetime import datetime

bot = Bot(TOKEN)


def status_merge(status_old, status):
    if status_old == "ok" or status == "ok":
        return "ok"
    elif status_old == "fail" and status == "fail":
        return "fail"
    else:
        return "down"


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

    last_checks = list(db.checks.find({}, sort=[("ts", DESC)]).limit(2))
    
    while len(last_checks) < 2:
        last_checks.append({"ip": "", "result": {}})
    
    last_ip = last_checks[0]["ip"]
    
    ip = network.resolve(HOST)

    if ip != last_ip:
        notify("\ud83d\udd01 *{host}* has new IP address: *{ip}*".format(host=HOST, ip=ip))

    result = {}

    for client in db.clients.find({}):
        client_ip, cn = client["ip"], client["cn"]

        if not client_ip:
            verdict = "down"
        elif network.connect(ip, 1080, client_ip):
            verdict = "ok"
        elif network.connect(network.resolve(DUMMY_HOST), 80, client_ip):
            verdict = "fail"
        else:
            verdict = "down"

        result[cn] = verdict
        old_results = [item["result"].get(cn, "down") for item in last_checks]

        old_status = status_merge(*old_results)
        status = status_merge(old_results[0], verdict)

        if status != old_status:
            bot.send_message(
                    chat_id=client["owner"],
                    text="{emoji} Your client *{cn}* {state}".format(
                        emoji=EMOJI[status], 
                        cn=cn, 
                        state=INFO[status]
                    ),
                    parse_mode="Markdown"
            )
            
        if status == "fail" and old_status == "ok":
            notify("\u274c Failed to connect via *{cn}* to *{host}* ({ip})".format(
                cn=cn, 
                host=HOST, 
                ip=ip
            ))

        if status == "ok" and old_status == "fail":
            notify("\u2705 Client *{cn}* restored connection to *{host}* ({ip})".format(
                cn=cn, 
                host=HOST, 
                ip=ip
            ))
    
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
        except KeyboardInterrupt:
            print("Exit by Ctrl-C", flush=True)
            break
        except:
            traceback.print_exc()
            continue

        st = {"ok": 0, "fail": 0, "down": 0}
        for client in result:
            st[result[client]] += 1

        print(datetime.fromtimestamp(time()).strftime('%H:%M:%S'), "- checking", ip, "-", st["ok"], "succeeded,", st["fail"], "failed,", st["down"], "down", flush=True)

        sleep(30)

if __name__ == "__main__":
    main()

