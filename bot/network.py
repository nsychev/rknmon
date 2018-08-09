from socket import socket, gethostbyname, error as SocketError
from subprocess import call as system_call, DEVNULL
from platform import system as system_name
import os

# WARNING: IMPORTING THIS MODULE MAY BROKE YOUR PROGRAM
os.setgid(0x80000000 + os.getpid())


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
    # RULE = ["iptables", "-t", "mangle", "-I", "PREROUTING", "-d", ip, "-m", "owner", "--gid-owner", str(os.getgid()), "-j", "MARK", "--set-mark", os.getpid()]
    RULE = ["ip", "route", "add", ip + "/32", "via", gateway]
    system_call(RULE, stdout=DEVNULL)

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
    
    RULE[2] = "del" #RULE[3] = "-D"
    system_call(RULE, stdout=DEVNULL)

    return result

