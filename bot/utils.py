from platform import system as system_name
from subprocess import call, DEVNULL
from pyroute2 import IPRoute
from socket import socket, gethostbyname as resolve, error as SocketError

ipr = IPRoute()


def get_ip(host):
    try:
        return resolve(host)
    except SocketError:
        return ""


def ping(host):
    param = "-n" if system_name().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    return call(command, stdout=DEVNULL) == 0


def sock_connect(ip, port, route_via):
    try:
        ipr.route("add", dst=ip+"/32", gateway=route_via)
        s = socket()
        s.settimeout(2)
        s.connect((ip, port))
        s.close()
    except SocketError:
        return False
    finally:
        ipr.route("del", dst=ip+"/32", gateway=route_via)

    return True

