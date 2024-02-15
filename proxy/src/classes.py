from watchdog.events import RegexMatchingEventHandler
from src.filter_modules import import_modules
from dataclasses import dataclass
from typing import List


class ModuleWatchdog(RegexMatchingEventHandler):
    def __init__(self, regexes, in_module, out_module, name):
        self.in_module = in_module
        self.out_module = out_module
        self.name = name
        super().__init__(regexes=regexes)

    def on_modified(self, event):
        print(self.name, "RELOADING", {event.src_path})
        try:
            self.in_module, self.out_module = import_modules(self.name)
        except Exception as e:
            print(self.name, "ERROR in reloading:", str(e))


@dataclass
class SSLConfig:
    server_certificate: str
    server_key: str
    client_certificate: str = None
    client_key: str = None
    ca_file: str = None


class Service:
    def __init__(self, name: str, target_ip: str, target_port: int, listen_port: int, listen_ip: str = "::", http = False, ssl=None):
        self.name = name
        self.target_ip = target_ip
        self.target_port = target_port
        self.listen_port = listen_port
        self.listen_ip = listen_ip
        self.http = http
        if ssl:
            self.ssl = SSLConfig(**ssl)
        else:
            self.ssl = None


@dataclass
class Config:
    services: List[Service]
    global_config: dict
