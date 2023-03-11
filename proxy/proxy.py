#!/usr/bin/env  python3
import argparse
import os
import sys
import threading
import socket
import ssl
import time
import select
import errno
import copy
import importlib
import traceback
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from multiprocessing import Process, Value

TARGET_IPS = os.getenv("TARGET_IPS", default="").replace(" ", "").split(",")
TARGET_PORTS = os.getenv("TARGET_PORTS", default="").replace(" ", "").split(",")
LISTEN_PORTS = os.getenv("LISTEN_PORTS", default="").replace(" ", "").split(",")
KEYWORD = os.getenv("KEYWORD", default="EH VOLEVIH")
VERBOSE = True if os.getenv("VERBOSE", default="false") == "true" else False

class fileWatchdog(RegexMatchingEventHandler):
    def __init__(self, regexes, in_module, out_module, name):
        self.in_module = in_module
        self.out_module = out_module
        self.name = name
        super().__init__(regexes = regexes)
    def on_modified(self, event):
        print(self.name, "RELOADING", {event.src_path})
        try:
            self.in_module,self.out_module = import_modules(self.name)
        except Exception as e:
            print(self.name, "ERROR in reloading:", str(e))

def parse_args():
    parser = argparse.ArgumentParser(description='Simple TCP proxy for data ' +
                                                 'interception')

    parser.add_argument('-ti', '--target-ips', dest='target_ip', nargs='+',
                        default=TARGET_IPS,
                        help='remote targets IPs or host names')

    parser.add_argument('-tp', '--target-ports', dest='target_port', nargs='+',
                        default=TARGET_PORTS,
                        help='remote targets ports')

    parser.add_argument('-li', '--listen-ip', dest='listen_ip',
                        default='0.0.0.0', help='IP address/host name to listen for ' +
                        'incoming data')

    parser.add_argument('-lp', '--listen-ports', dest='listen_port', nargs='+',
                        default=LISTEN_PORTS,
                        help='ports to listen on')
    
    parser.add_argument('-k', '--keyword', dest='keyword',
                        default=KEYWORD, 
                        help='Keyword to use as a response for malicious packets to' + 
                        'quickly find them in a pcap file')

    parser.add_argument('-v', '--verbose', dest='verbose', default=VERBOSE,
                        action='store_true',
                        help='More verbose output of status information')

    parser.add_argument('-s', '--ssl', dest='use_ssl', action='store_true',
                        default=False, help='detect SSL/TLS as well as STARTTLS')

    parser.add_argument('-sc', '--server-certificate', default='mitm.pem',
                        help='server certificate in PEM format (default: %(default)s)')

    parser.add_argument('-sk', '--server-key', default='mitm.pem',
                        help='server key in PEM format (default: %(default)s)')

    parser.add_argument('-cc', '--client-certificate', default=None,
                        help='client certificate in PEM format in case client authentication is required by the target')

    parser.add_argument('-ck', '--client-key', default=None,
                        help='client key in PEM format in case client authentication is required by the target')

    return parser.parse_args()

def generate_module_file(targetIPs):    
    with open("./proxymodules/template.py", "rt") as template:
        templateLines = template.readlines()
        basePath = "./proxymodules/services/"
        try:
            os.mkdir(basePath)
        except FileExistsError:
            pass
        modules = os.listdir(basePath)
        for name in targetIPs:
            name = name.replace(".", "-")
            if name+"_in.py" not in modules:
                #output file to write the result to
                fout_in = open(basePath + name + "_in.py", "wt+")
                #for each line in the input file
                for line in templateLines:
                    #read replace the string and write to output file
                    fout_in.write(line.replace('template', name + "_in"))
                #close input and output files
                fout_in.close()
                os.chmod(basePath + name + "_in.py", 0o777)
            if name+"_out.py" not in modules:
                fout_out = open(basePath + name + "_out.py", "wt+")
                for line in templateLines:
                    fout_out.write(line.replace('template', name+ "_out"))
                fout_out.close()
                os.chmod(basePath + name + "_out.py", 0o777)

def import_modules(name, reload=True):
    basePath = "proxymodules.services."
    try:
        if reload:
            importlib.reload(importlib.import_module((basePath + name + "_in")))
            importlib.reload(importlib.import_module((basePath + name + "_out")))
        else:
            __import__(basePath + name + "_in")
            __import__(basePath + name + "_out")
        in_module = sys.modules[basePath + name + "_in"].Module()
        out_module = sys.modules[basePath + name + "_out"].Module()
    except ImportError as e:
        print('Module %s not found' % name)
        print(e.msg)
        sys.exit(3)
    return in_module, out_module

def receive_from(s):
    """Receive data from a socket until no more data is there"""
    b = b""
    while True:
        data = s.recv(4096)
        b += data
        if not data or len(data) < 4096:
            break
    return b

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

def enable_ssl(args, remote_socket, local_socket):
    sni = None

    def sni_callback(sock, name, ctx):
        nonlocal sni
        sni = name

    try:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.sni_callback = sni_callback
        ctx.load_cert_chain(certfile=args.server_certificate,
                            keyfile=args.server_key,
                            )
        local_socket = ctx.wrap_socket(local_socket,
                                       server_side=True,
                                       )
    except ssl.SSLError as e:
        print("SSL handshake failed for listening socket", str(e))
        raise

    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if args.client_certificate and args.client_key:
            ctx.load_cert_chain(certfile=args.client_certificate,
                                keyfile=args.client_key,
                                )
        remote_socket = ctx.wrap_socket(remote_socket,
                                        server_hostname=sni,
                                        )
    except ssl.SSLError as e:
        print("SSL handshake failed for remote socket", str(e))
        raise

    return [remote_socket, local_socket]

def starttls(args, local_socket, read_sockets):
    return (args.use_ssl and
            local_socket in read_sockets and
            not isinstance(local_socket, ssl.SSLSocket) and
            is_client_hello(local_socket)
            )

def start_proxy_thread(local_socket, args, in_module, out_module, count):
    """This method is executed in a thread. It will relay data between the local
    host and the remote host, while letting modules work on the data before
    passing it on."""
    remote_socket = socket.socket()

    try:
        remote_socket.connect((args.target_ip, args.target_port))
        vprint('Connected to %s:%d' % remote_socket.getpeername(), args.verbose)
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            for s in [remote_socket, local_socket]:
                s.close()
            print(f'{time.strftime("%Y%m%d-%H%M%S")}, {args.target_ip}:{args.target_port}- Connection refused')
            return None
        elif serr.errno == errno.ETIMEDOUT:
            for s in [remote_socket, local_socket]:
                s.close()
            print(f'{time.strftime("%Y%m%d-%H%M%S")}, {args.target_ip}:{args.target_port}- Connection timed out')
            return None
        else:
            for s in [remote_socket, local_socket]:
                s.close()
            raise serr

    # This loop ends when no more data is received on either the local or the
    # remote socket
    running = True
    while running:
        read_sockets, _, _ = select.select([remote_socket, local_socket], [], [])

        if starttls(args, local_socket, read_sockets):
            try:
                ssl_sockets = enable_ssl(args, remote_socket, local_socket)
                remote_socket, local_socket = ssl_sockets
                vprint("SSL enabled", args.verbose)
            except ssl.SSLError as e:
                print("SSL handshake failed", str(e))
                break

            read_sockets, _, _ = select.select(ssl_sockets, [], [])

        for sock in read_sockets:
            try:
                peer = sock.getpeername()
            except socket.error as serr:
                if serr.errno == errno.ENOTCONN:
                    print(f"{time.strftime('%Y%m%d-%H%M%S')}: Socket error (ENOTCONN) in start_proxy_thread")
                    for s in [remote_socket, local_socket]:
                        s.close()
                    running = False
                    break
                else:
                    print(f"{time.strftime('%Y%m%d-%H%M%S')}: Socket exception in start_proxy_thread")
                    raise serr

            try:
                data = receive_from(sock)
            except socket.error as serr:
                vprint(f"{time.strftime('%Y%m%d-%H%M%S')}: Socket exception in start_proxy_thread: connection reset by local or remote host")
                remote_socket.close()
                local_socket.close()
                running = False
                break
            
            vprint('Received %d bytes' % len(data), args.verbose)

            if sock == local_socket:
                if len(data):
                    # going to service
                    vprint(b'< < < in\n' + data, args.verbose)
                    lineToSend = ""
                    if in_module is not None:
                        try:
                            attack = in_module.execute(data)
                            if attack is not None:
                                count.value += 1
                                data = None
                                lineToSend = KEYWORD + "\n" + args.target_ip + " " + attack
                        except:
                            traceback.print_exc()
                    if data is not None:
                        remote_socket.send(data.encode() if isinstance(data, str) else data)
                    else:
                        vprint("Connection from local client %s:%d closed" % peer, args.verbose)
                        remote_socket.close()
                        local_socket.send(lineToSend.encode())
                        local_socket.close()
                        running = False
                        break
                else:
                    vprint("Connection from local client %s:%d closed" % peer, args.verbose)
                    remote_socket.close()
                    running = False
                    break
            elif sock == remote_socket:
                if len(data):
                    # going to client
                    vprint(b'> > > out\n' + data, args.verbose)
                    if out_module is not None:
                        try:
                            attack = out_module.execute(data)
                            if attack is not None:
                                count.value += 1
                                data = None
                                lineToSend = KEYWORD + "\n" + args.target_ip + " " + attack
                        except:
                            traceback.print_exc()
                    if data is not None:
                        local_socket.send(data)
                    else:
                        vprint("Connection to remote server %s:%d closed" % peer, args.verbose)
                        remote_socket.close()
                        local_socket.send(lineToSend.encode())
                        local_socket.close()
                        running = False
                        break
                else:
                    vprint("Connection to remote server %s:%d closed" % peer, args.verbose)
                    local_socket.close()
                    running = False
                    break

def vprint(msg, is_verbose):
    """ this will print msg, but only if is_verbose is True"""
    if is_verbose:
        print(msg)

def serviceFunction(args_process, count):
    # print(args_process.target_ip)
    module_name = args_process.target_ip.replace(".", "-")
    in_module, out_module = import_modules(module_name, False)
    
    # this event handler will reload modules on changes
    watchdog_handler = fileWatchdog(regexes=[f".*{module_name}.*\.py"], in_module = in_module, out_module = out_module, name = module_name)            
    observer = Observer()
    observer.schedule(watchdog_handler, path='./proxymodules/services/', recursive=False)
    observer.start()

    # this is the socket we will listen on for incoming connections
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        proxy_socket.bind((args_process.listen_ip, args_process.listen_port))
    except socket.error as e:
        print(e.strerror)
        sys.exit(5)
    proxy_socket.listen(100)
    vprint(str(args_process), args_process.verbose)

    # endless loop until ctrl+c
    try:
        while True:
            in_socket, in_addrinfo = proxy_socket.accept()
            in_module = watchdog_handler.in_module
            out_module = watchdog_handler.out_module
            vprint('Connection from %s:%d' % in_addrinfo, args_process.verbose)
            proxy_thread = threading.Thread(target=start_proxy_thread,
                                            args=(
                                                in_socket, args_process, in_module,
                                                out_module, count
                                            ))
            vprint("Starting proxy thread " + proxy_thread.name, args_process.verbose)
            proxy_thread.start()

    except KeyboardInterrupt:
        vprint('Ctrl+C detected, exiting...', args_process.verbose)
        observer.stop()
        observer.join()
        sys.exit(0)

def main():
    args = parse_args()
    if not args.target_ip or args.target_ip[0] == "":
        print('Target IPs are required: -ti')
        sys.exit(6)
    if not args.target_port or args.target_port[0] == "":
        print('Target ports are required: -tp')
        sys.exit(7)
    if not args.listen_port or args.listen_port[0] == "":
        print('Listen ports are required: -lp')
        sys.exit(7)

    if len(args.target_ip) != len(args.target_port) or len(args.target_ip) != len(args.listen_port):
        print("Target IPs, target ports and listen ports must be the same number")
        sys.exit(7)
    
    if ((args.client_key is None) ^ (args.client_certificate is None)):
        print("You must either specify both the client certificate and client key or leave both empty")
        sys.exit(8)

    args_processes = []

    for i in range (len(args.listen_port)):
        args_processes.append(copy.deepcopy(args))
        args_processes[i].listen_port = int(args.listen_port[i])
        args_processes[i].target_ip = args.target_ip[i]
        args_processes[i].target_port = int(args.target_port[i])

    generate_module_file(args.target_ip)

    nPackets = []

    try:
        with open("./log.txt", "r") as f:
            lines = f.readlines()[1:]
            for args_process in args_processes:
                value = 0
                for line in lines:
                    if args_process.target_ip == line.split(":")[0].strip():
                        value = int(line.split()[-1].strip())
                nPackets.append(Value('i', value))
    except FileNotFoundError:
        print("Log file not found")
        for i in range(len(args_processes)):
            nPackets.append(Value('i', 0))

    processes = []
    for index, args_process in enumerate(args_processes):
        processes.append(Process(target=serviceFunction, args=(args_process, nPackets[index])))
    
    for process in processes:
        process.start()

    while True:
        time.sleep(2)
        try:
            with open("./log.txt", "w") as f:
                lines = ["Packets blocked:\n"]
                for index, args_process in enumerate(args_processes):
                    lines.append(f"{args_process.target_ip}: {nPackets[index].value}\n")
                f.writelines(lines)
        except KeyboardInterrupt:
            break
        except:
            print("Error in opening log file")
    for process in processes:
        process.join()

if __name__ == '__main__':
    main()
