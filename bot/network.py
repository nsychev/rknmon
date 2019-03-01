from socket import socket, gethostbyname
from dns.resolver import Resolver
from subprocess import call as system_call, DEVNULL
from platform import system as system_name
import os
import sys
import traceback

# WARNING: IMPORTING THIS MODULE MAY BROKE YOUR PROGRAM
GID = 0x80000000 + os.getpid()
os.setgid(GID)
GID = str(GID)

RESOLVERS = ["213.180.204.213", "93.158.134.213", "77.88.8.8"]


# ensure - returns True after the first success, or False in case of three fails
def ensure(func):
    return func() or func() or func()


# ping - pings host
def ping(host):
    param = "-n" if system_name().lower() == "windows" else "-c"
    return ensure(lambda: system_call(
        ["ping", param, "1", host],
        stdout=DEVNULL
    ) == 0)


def resolve(host):
    try:
        resolver = Resolver()
        resolver.nameservers = RESOLVERS

        answer = resolver.query(host, "A")

        return str(answer.rrset.items[0])
    except Exception as e:
        print("Fallback to legacy resolver", str(e), file=sys.stderr)
        return resolve_legacy(host)
    
def resolve_legacy(host):
    try:
        return gethostbyname(host)
    except OSError:
        return ""


def connect(ip, port, gateway):
    cmd_iptables = ["iptables", "-t", "mangle", "-I", "OUTPUT", "-m", "owner", "--gid-owner", GID, "-j", "MARK", "--set-mark", GID]
    # TODO: use pyroute2
    cmd_rule = ["ip", "rule", "add", "fwmark", GID, "table", GID]
    cmd_route = ["ip", "route", "add", ip + "/32", "via", gateway, "table", GID]

    system_call(cmd_iptables, stdout=DEVNULL)
    system_call(cmd_rule, stdout=DEVNULL)
    system_call(cmd_route, stdout=DEVNULL)

    def can_connect():
        try:
            s = socket()
            s.settimeout(2)
            s.connect((ip, port))
            s.close()
            return True
        except OSError as e:
            traceback.print_exc()
            s.close()
            print("Error {error} while connecting to {ip}:{port} via {gw}".format(
                error=e.errno,
                ip=ip,
                port=port,
                gw=gateway
            ), file=sys.stderr, flush=True)
            return False

    result = ensure(can_connect)
    
    cmd_iptables[3] = "-D"
    cmd_rule[2] = "del"
    cmd_route[2] = "del"

    system_call(cmd_iptables, stdout=DEVNULL)
    system_call(cmd_rule, stdout=DEVNULL)
    system_call(cmd_route, stdout=DEVNULL)

    return result

