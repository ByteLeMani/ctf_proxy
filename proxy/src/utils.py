import json
from src.classes import Config, Service
import socket
import ssl
import traceback
from http.client import parse_headers
import time


def getConfig(path) -> Config:
    with open(path, "r") as f:
        x = json.load(f)
        x["services"] = [Service(**service) for service in x["services"]]
        return Config(**x)


def vprint(msg, is_verbose):
    """ this will print msg, but only if is_verbose is True"""
    if is_verbose:
        print(msg)

def receive_from(s: socket.socket, http, verbose=False):
    """Receive data from a socket until no more data is there"""
    b = b""
    if not http:
        while True:
            data = s.recv(4096)
            b += data
            if not data or len(data) < 4096:
                break
    else:
        with s.makefile(mode = "rb", buffering=True) as fp:
            b += fp.readline()
            if len(b) == 0:
                return b
            
            # read headers
            content_len = 0
            chunked = False
            len_headers = 0
            while True:
                line = fp.readline(65537)
                len_headers += 1
                if len(line) > 65536:
                    vprint("Header line too long.", verbose)
                    return b""
                if len_headers > 100:
                    vprint("Too many headers", verbose)
                    return b""
                b += line
                if line in (b'\r\n', b'\n', b''):
                    break
                line = line.decode().lower()
                if "content-length" in line:
                    content_len = int(line.split(":")[1])
                elif "transfer-encoding" in line:
                    chunked = "chunked" in line

            if content_len:
                content_len = int(content_len)
                b += fp.read(content_len)
            elif chunked:
                while True:
                    line = fp.readline()
                    b+= line
                    line = line.strip()
                    chunk_length = int(line, 16)

                    if chunk_length != 0:
                        chunk = fp.read(chunk_length)
                        b += chunk
                    # Each chunk is followed by an additional empty newline
                    # that we have to consume.
                    b += fp.readline()

                    # Finally, a chunk size of 0 is an end indication
                    if chunk_length == 0:
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


def block_packet(local_socket: socket.socket, socket_family, remote_socket, block_answer: str, dos: dict = None):
    remote_socket.close()
    if isinstance(local_socket, ssl.SSLSocket):
        local_socket = socket.fromfd(
            local_socket.detach(), socket_family, socket.SOCK_STREAM)

    local_socket.send(block_answer.encode())
    if dos.get("enabled"):
        start = time.time()
        try:
            while time.time() - start < dos["duration"]:
                local_socket.sendall(b".")
                time.sleep(dos["interval"])
        except Exception as e:
            # socket has been closed by client
            pass
    local_socket.close()



