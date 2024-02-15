
import ssl
import socket
from src.constants import CERTIFICATES_PATH
import os


def is_client_hello(sock):
    firstbytes = sock.recv(128, socket.MSG_PEEK)
    return (len(firstbytes) >= 3 and
            firstbytes[0] == 0x16 and
            firstbytes[1:3] in [b"\x03\x00",
                                b"\x03\x01",
                                b"\x03\x02",
                                b"\x03\x03",
                                b"\x02\x00"]
            )


def enable_ssl(ssl_config, remote_socket, local_socket):
    sni = None

    def sni_callback(sock, name, ctx):
        nonlocal sni
        sni = name

    try:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.sni_callback = sni_callback
        ctx.load_cert_chain(certfile=os.path.join(CERTIFICATES_PATH, ssl_config.server_certificate),
                            keyfile=os.path.join(CERTIFICATES_PATH, ssl_config.server_key)
                            )
        if ssl_config.ca_file:
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(cafile=os.path.join(CERTIFICATES_PATH, ssl_config.ca_file))
        local_socket = ctx.wrap_socket(local_socket,
                                       server_side=True,
                                       suppress_ragged_eofs=True
                                       )
    except ssl.SSLError as e:
        if e.reason != "SSLV3_ALERT_CERTIFICATE_UNKNOWN":
            print("SSL handshake failed for listening socket", str(e))
        raise

    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if ssl_config.client_certificate and ssl_config.client_key:
            ctx.load_cert_chain(certfile=os.path.join(CERTIFICATES_PATH, ssl_config.client_certificate),
                                keyfile=os.path.join(CERTIFICATES_PATH, ssl_config.client_key)
                                )
        remote_socket = ctx.wrap_socket(remote_socket,
                                        server_hostname=sni,
                                        suppress_ragged_eofs=True
                                        )
    except ssl.SSLError as e:
        print("SSL handshake failed for remote socket", str(e))
        raise

    return [remote_socket, local_socket]


def start_tls(ssl_config, local_socket, read_sockets):
    return (ssl_config and
            local_socket in read_sockets and
            not isinstance(local_socket, ssl.SSLSocket) and
            is_client_hello(local_socket)
            )
