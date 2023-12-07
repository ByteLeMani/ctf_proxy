import json
from ipaddress import ip_address, IPv4Address 

CFG_PATH="proxy/config/config.json"
NGINX_CONF_PATH="nginx/nginx.conf"

def validIPAddress(IP: str) -> str: 
    try: 
        return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
    except ValueError: 
        return "Invalid"

with open(CFG_PATH) as f:
    cfg = json.load(f)

services = cfg["services"]
fail_timeout = cfg["global_config"].get("failover_timeout", 5)

nginx_conf = '''
worker_processes auto;

events {{ 
    worker_connections 1024; 
}}

stream {{
    {}
}}
'''

template = """
    upstream {service_name} {{
        server proxy:{target_port} fail_timeout={fail_timeout};
        server {target_ip}:{target_port} backup;
    }}
    server {{
        listen {listen_ip}:{listen_port};
        proxy_pass {service_name};
    }}
"""

config = ""

for service in services:
    listen_ip = service.get("listen_ip", "0.0.0.0")
    if validIPAddress(listen_ip) == "IPv6":
        listen_ip = "[" + listen_ip + "]"
		
    config += template.format(service_name = service["name"] + "_upstream",
                             target_ip = service["target_ip"],
                             target_port = service["target_port"],
                             listen_ip = listen_ip,
                             listen_port = service["listen_port"],
                             fail_timeout = fail_timeout
                             )
    
with open(NGINX_CONF_PATH, "w") as f:
    f.write(nginx_conf.format(config))