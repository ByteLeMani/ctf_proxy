import sys
import threading
import socket
import ssl
import time
import select
import errno
from watchdog.observers import Observer
from src.filter_modules import import_modules
from src.classes import FileWatchdog, Service
import src.constants as constants
import os
import src.utils as utils
import src.ssl_utils as ssl_utils


def service_function(service: Service, global_config, count):
    in_module, out_module = import_modules(service.name, False)

    # this event handler will reload modules on changes
    watchdog_handler = FileWatchdog(regexes=[f".*{service.name}.*\.py"], in_module=in_module,
                                    out_module=out_module, name=service.name)
    observer = Observer()
    observer.schedule(watchdog_handler, path=os.path.join(constants.MODULES_PATH, service.name), recursive=False)
    observer.start()

    # this is the socket we will listen on for incoming connections
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        proxy_socket.bind((service.listen_ip, service.listen_port))
    except socket.error as e:
        print(e.strerror)
        sys.exit(5)
    proxy_socket.listen(100)
    utils.vprint(service.__dict__, global_config["verbose"])

    # endless loop until ctrl+c
    try:
        while True:
            in_socket, in_addrinfo = proxy_socket.accept()
            in_module = watchdog_handler.in_module
            out_module = watchdog_handler.out_module
            utils.vprint('Connection from %s:%d' %
                         in_addrinfo, global_config["verbose"])
            proxy_thread = threading.Thread(target=connection_thread,
                                            args=(
                                                in_socket, service, global_config,
                                                in_module, out_module, count
                                            ))
            utils.vprint("Starting proxy thread " +
                         proxy_thread.name, global_config["verbose"])
            proxy_thread.start()

    except KeyboardInterrupt:
        utils.vprint('Ctrl+C detected, exiting...', global_config["verbose"])
        observer.stop()
        observer.join()
        sys.exit(0)


def connection_thread(local_socket: socket.socket, service: Service, global_config, in_module, out_module, count):
    """This method is executed in a thread. It will relay data between the local
    host and the remote host, while letting modules work on the data before
    passing it on."""
    remote_socket = socket.socket()

    try:
        remote_socket.connect((service.target_ip, service.target_port))
        utils.vprint('Connected to %s:%d' %
                     remote_socket.getpeername(), global_config["verbose"])
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            for s in [remote_socket, local_socket]:
                s.close()
            print(
                f'{time.strftime("%Y%m%d-%H%M%S")}, {service.target_ip}:{service.target_port}- Connection refused')
            return None
        elif serr.errno == errno.ETIMEDOUT:
            for s in [remote_socket, local_socket]:
                s.close()
            print(
                f'{time.strftime("%Y%m%d-%H%M%S")}, {service.target_ip}:{service.target_port}- Connection timed out')
            return None
        else:
            for s in [remote_socket, local_socket]:
                s.close()
            raise serr

    # This loop ends when no more data is received on either the local or the
    # remote socket
    connection_open = True
    while connection_open:
        ready_sockets, _, _ = select.select(
            [remote_socket, local_socket], [], [])
        if ssl_utils.start_tls(service.ssl, local_socket, ready_sockets):
            try:
                ssl_sockets = ssl_utils.enable_ssl(
                    service.ssl, remote_socket, local_socket)
                remote_socket, local_socket = ssl_sockets
                utils.vprint("SSL enabled", global_config["verbose"])
            except ssl.SSLError as e:
                if e.reason != "SSLV3_ALERT_CERTIFICATE_UNKNOWN":
                    print("SSL handshake failed", str(e))
                break

            ready_sockets, _, _ = select.select(ssl_sockets, [], [])

        for sock in ready_sockets:
            try:
                peer = sock.getpeername()
            except socket.error as serr:
                if serr.errno == errno.ENOTCONN:
                    print(
                        f"{time.strftime('%Y%m%d-%H%M%S')}: Socket error (ENOTCONN) in connection_thread")
                    for s in [remote_socket, local_socket]:
                        s.close()
                    connection_open = False
                    break
                else:
                    print(
                        f"{time.strftime('%Y%m%d-%H%M%S')}: Socket exception in connection_thread")
                    raise serr

            try:
                data = utils.receive_from(sock)
            except socket.error as serr:
                utils.vprint(
                    f"{time.strftime('%Y%m%d-%H%M%S')}: Socket exception in connection_thread: connection reset by local or remote host")
                remote_socket.close()
                local_socket.close()
                connection_open = False
                break

            utils.vprint('Received %d bytes' %
                         len(data), global_config["verbose"])

            if sock == local_socket:
                # going from client to service
                if not len(data):
                    utils.vprint("Connection from local client %s:%d closed" %
                                 peer, global_config["verbose"])
                    remote_socket.close()
                    connection_open = False
                    break

                utils.vprint(b'> > > in\n' + data, global_config["verbose"])
                attack = utils.filter_packet(data, in_module)
                if not attack:
                    remote_socket.send(data)
            else:
                # going from service to client
                if not len(data):
                    utils.vprint("Connection from remote server %s:%d closed" %
                                 peer, global_config["verbose"])
                    local_socket.close()
                    connection_open = False
                    break

                utils.vprint(b'< < < out\n' + data, global_config["verbose"])
                attack = utils.filter_packet(data, out_module)
                if not attack:
                    local_socket.send(data)

            if attack:
                utils.vprint("Connection %s:%d BLOCKED" %
                             peer, global_config["verbose"])
                count.value += 1
                block_answer = global_config["keyword"] + \
                    "\n" + service.name + " " + attack
                utils.block_packet(local_socket, remote_socket, block_answer)
                connection_open = False
                break
