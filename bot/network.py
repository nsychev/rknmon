from socket import socket, gethostbyname, error as SocketError
from subprocess import call as system_call, DEVNULL
from platform import system as system_name
import os

# WARNING: IMPORTING THIS MODULE MAY BROKE YOUR PROGRAM
GID = 0x80000000 + os.getpid()
os.setgid(GID)
GID = str(GID)


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
        return gethostbyname(host)
    except SocketError:
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
        except SocketError:
            s.close()
            return False

    result = ensure(can_connect)
    
    cmd_iptables[3] = "-D"
    cmd_rule[2] = "del"
    cmd_route[2] = "del"

    system_call(cmd_iptables, stdout=DEVNULL)
    system_call(cmd_rule, stdout=DEVNULL)
    system_call(cmd_route, stdout=DEVNULL)

    return result

