import json

CFG_PATH="config/config.json"
NGINX_CONF_PATH="/nginx.conf"

with open(CFG_PATH) as f:
    cfg = json.load(f)

services = cfg["services"]
fail_timeout = cfg["global_config"]["nginx"].get("fail_timeout", 5)
max_fails = cfg["global_config"]["nginx"].get("max_fails", 5)
connect_timeout = cfg["global_config"]["nginx"].get("connect_timeout", 5)

nginx_conf = '''worker_processes auto;

events {{ 
    worker_connections 1024; 
}}

stream {{
    {}
}}
'''

template = """
    upstream {service_name} {{
        server proxy:{target_port} fail_timeout={fail_timeout}s max_fails={max_fails};
        server {target_ip}:{target_port} backup;
    }}
    server {{
        proxy_connect_timeout {connect_timeout}s;
        listen {listen_port};
        listen [::]:{listen_port};
        proxy_pass {service_name};
    }}
"""

config = ""

for service in services:
    config += template.format(service_name = service["name"] + "_upstream",
                             target_ip = service["target_ip"],
                             target_port = service["target_port"],
                             listen_port = service["listen_port"],
                             connect_timeout = connect_timeout,
                             max_fails = max_fails,
                             fail_timeout = fail_timeout
                             )
    
with open(NGINX_CONF_PATH, "w") as f:
    f.write(nginx_conf.format(config))