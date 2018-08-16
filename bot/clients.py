from decorators import *
from config import *
from database import db
from subprocess import run as system_exec, DEVNULL
import os


# /generate - generates VPN keypair and config
@only_admin
def generate(bot, update, args):
    if len(args) != 1:
        update.message.reply_text("\u274c Usage: /generate [common_name]")

    common_name = args[0]

    result = system_exec([os.path.join(BASE_DIR, "scripts", "create.sh"), common_name], capture_output=True)
    
    # TODO: rewrite to Pythonic-way
    update.message.reply_html("<pre>{}</pre>".format(result.stdout.decode()))


# /register - gives pre-generated VPN config to Telegram user and associates them
@only_pm
def register(bot, update, args):
    if len(args) != 1:
        update.message.reply_text("\u274c Usage: /register [common_name]")
        return

    common_name = args[0]

    if db.clients.find_one({"cn": common_name}) is not None:
        update.message.reply_text("\u274c This client is already registered")
        return

    if not CN_RE.match(common_name):
        update.message.reply_text("\u274c CN is invalid")
        return

    conf_path = os.path.join(BASE_DIR, "conf", "output", "{cn}.conf".format(cn=common_name))
    
    if not os.path.exists(conf_path):
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
– using iptables: <code>iptables -I FORWARD -d {host} -j DROP</code>
– replace <code>-I</code> with <code>-D</code> to undo it

Questions? @nsychev'''.format(cn=common_name, host=HOST), disable_web_page_preview=True)

    with open(conf_path, "rb") as conf_file:
        update.message.reply_document(conf_file)


# /revoke - clears host from DB
@only_admin
def revoke(bot, update, args):
    if len(args) != 1:
        update.message.reply_text("usage: /revoke [common_name]")
        return
    
    common_name = args[0]

    client = db.clients.find_one_and_delete({"cn": common_name})
    bot.send_message(chat_id=client["owner"], text="\u274c Your account for *{cn}* was revoked by admin".format(cn=common_name), parse_mode="Markdown")
    update.message.reply_markdown("\u2705 Account *{cn}* was revoked.\n\nThis action doesn't imply VPN certificate revokation".format(cn=common_name))


