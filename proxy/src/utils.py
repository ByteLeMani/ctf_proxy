import json
from src.classes import Config, Service
import socket
import ssl
import traceback


def getConfig(path) -> Config:
    with open(path, "r") as f:
        x = json.load(f)
        x["services"] = [Service(**service) for service in x["services"]]
        return Config(**x)


def vprint(msg, is_verbose):
    """ this will print msg, but only if is_verbose is True"""
    if is_verbose:
        print(msg)


def receive_from(s):
    """Receive data from a socket until no more data is there"""
    b = b""
    while True:
        data = s.recv(4096)
        b += data
        if not data or len(data) < 4096:
            break
    return b


def filter_packet(data, filter_module):
    if filter_module is not None:
        try:
            attack = filter_module.execute(data)
            if attack is not None:
                return attack
        except:
            traceback.print_exc()
    return None


def block_packet(local_socket, remote_socket, block_answer):
    remote_socket.close()
    if isinstance(local_socket, ssl.SSLSocket):
        local_socket = socket.fromfd(
            local_socket.detach(), socket.AF_INET, socket.SOCK_STREAM)
    local_socket.send(block_answer.encode())
    local_socket.close()
