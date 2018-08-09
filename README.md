# RKN Monitor

Service which analyzes how Internet censorship in Russia works.
It tries to determine when exactly IP was banned, trying to connect there regularly via different network providers.

## How to build it

1. Clone this repository to your server. Let call directory you cloned the repo `$BASE_DIR`.

2. Install dependencies: OpenVPN, EasyRSA, Python 3, MongoDB and some stuff from pip: pymongo, python-telegram-bot (TODO: reqirements.txt)

3. Buid your own CA in `$BASE_DIR/ca`: `make-cadir ca`

4. Generate server keypair, DH parameters and TA key.

5. Move that stuff along with `conf/server.conf`, `conf/connect.py` and `conf/disconnect.py` to `/etc/openvpn`

6. Ensure MongoDB is running at `127.0.0.1:27017`, without authorization.

7. Add configuration to `bot/config.py` (TODO: sample config)

8. Run OpenVPN, `bot/bot.py` and `bot/poll.py`

9. Generate client pack using `/generate` bot command. Do not do it using CA.

Clients need just to connect using provided VPN config.

## Credits

Author — Nikita Sychev, licensed [by MIT](LICENSE)


