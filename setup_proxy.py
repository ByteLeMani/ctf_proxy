#!/usr/bin/python3

import os
import json

import ruamel.yaml  # pip install ruamel.yaml

"""
Why not just use the included yaml package?
Because this one preservs order and comments (and also allows adding them)
"""

from pathlib import Path


yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=3, offset=1)

services_dict = {}


def parse_services():
    """
    If services.json is present, load it into the global dictionary.
    Otherwise, parse all the docker-compose yamls to build the dictionary and
    then save the result into services.json
    """
    dirs = []

    if Path("./services.json").exists():
        print("Found existing services file")
        with open("./services.json", "r") as fs:
            services_dict = json.load(fs)
    else:
        services_dict = {}
        for file in Path(".").iterdir():
            if (
                file.is_dir()
                and file.stem[0] != "."
                and file.stem
                not in ["remote_pcap_folder", "caronte", "tulip", "ctf_proxy"]
            ):
                dirs.append(Path(".", file))

        for service in dirs:
            file = Path(service, "docker-compose.yml")
            if not file.exists():
                file = Path(service, "docker-compose.yaml")

            with open(file, "r") as fs:
                ymlfile = yaml.load(file)

            for container in ymlfile["services"]:
                try:
                    ports_string = ymlfile["services"][container]["ports"]
                    ports_list = [p.split(":") for p in ports_string]

                    http = []
                    for port in ports_list:
                        http.append(
                            True
                            if "y"
                            in input(
                                f"Is the service {service.stem}:{port[-2]} http? (y/n) "
                            )
                            else False
                        )

                    container_dict = {
                        "target_port": [p[-1] for p in ports_list],
                        "listen_port": [p[-2] for p in ports_list],
                        "http": [h for h in http],
                    }
                    services_dict[service.stem] = {container: container_dict}

                except KeyError:
                    print(f"{service.stem}_{container} has no ports binding")
                except Exception as e:
                    raise e

        with open("services.json", "w") as backupfile:
            json.dump(services_dict, backupfile, indent=2)
    print("Found services:")
    for service in services_dict:
        print(f"\t{service}")
    return services_dict


def edit_services():
    """
    Prepare the docker-compose for each service; comment out the ports, add hostname, add the external network, add an external volume for data persistence (this alone isn't enough - it' s just for convenience since we are already here)
    """
    global services_dict

    for service in services_dict:
        file = Path(service, "docker-compose.yml")
        if not file.exists():
            file = Path(service, "docker-compose.yaml")

        with open(file, "r") as fs:
            ymlfile = yaml.load(file)

        for container in services_dict[service]:
            try:
                # Add a comment with the ports
                target_ports = services_dict[service][container]["target_port"]
                listen_ports = services_dict[service][container]["listen_port"]
                ports_string = "ports: "
                for target, listen in zip(target_ports, listen_ports):
                    ports_string += f"- {listen}:{target} "

                ymlfile["services"].yaml_add_eol_comment(ports_string, container)

                # Remove the actual port bindings
                try:
                    ymlfile["services"][container].pop("ports")
                except KeyError:
                    pass  # this means we had already had removed them

                # Add hostname
                hostname = f"{service}_{container}"
                ymlfile["services"][container]["hostname"] = hostname

            except Exception as e:
                print(ymlfile)
                raise e

            # TODO: Add restart: always

            # add external network
            ymlfile["networks"] = {"default": {"name": "ctf_network", "external": True}}

            # add external volume
            ymlfile["volumes"] = {
                "volume_persistente": {"name": "volume_persistente", "external": True}
            }

            # write file
            with open(file, "w") as fs:
                yaml.dump(ymlfile, fs)


def configure_proxy():
    """
    Properly configure both the proxy's docker-compose with the listening ports and the config.json with all the services.
    We can't automatically configure ssl for now, so it's better to set https services as not http so they keep working at least. Manually configure the SSL later and turn http back on.
    """
    global services_dict

    # Download ctf_proxy
    if not Path("./ctf_proxy").exists():
        os.system("git clone https://github.com/ByteLeMani/ctf_proxy.git")

    with open("./ctf_proxy/docker-compose.yml", "r") as file:
        ymlfile = yaml.load(file)

    # Add all the ports to the compose
    ports = []
    for service in services_dict:
        for container in services_dict[service]:
            for port in services_dict[service][container]["listen_port"]:
                ports.append(f"{port}:{port}")
    ymlfile["services"]["proxy"]["ports"] = ports
    with open("./ctf_proxy/docker-compose.yml", "w") as fs:
        yaml.dump(ymlfile, fs)

    # Proxy config.json
    print("Remember to manually edit the config for SSL")
    services = []
    for service in services_dict:
        for container in services_dict[service]:
            name = f"{service}_{container}"
            target_ports = services_dict[service][container]["target_port"]
            listen_ports = services_dict[service][container]["listen_port"]
            http = services_dict[service][container]["http"]
            for i, (target, listen) in enumerate(zip(target_ports, listen_ports)):
                services.append(
                    {
                        "name": name + str(i),
                        "target_ip": name,
                        "target_port": int(target),
                        "listen_port": int(listen),
                        "http": http[i],
                    }
                )

    with open("./ctf_proxy/proxy/config/config.json", "r") as fs:
        proxy_config = json.load(fs)
    proxy_config["services"] = services
    with open("./ctf_proxy/proxy/config/config.json", "w") as fs:
        json.dump(proxy_config, fs, indent=2)


def restart_services():
    global services_dict
    # With the config done, make sure every service is off and then start them one by one

    for service in services_dict:
        os.system(
            f"bash -c '!(docker compose --file {service}/docker-compose.yml down) && docker compose --file {service}/docker-compose.yaml down'"
        )

    os.system(
        f"bash -c 'docker compose --file ctf_proxy/docker-compose.yml restart; docker compose --file ctf_proxy/docker-compose.yml up -d'"
    )

    for service in services_dict:
        os.system(
            f"bash -c '!(docker compose --file {service}/docker-compose.yml up -d) && docker compose --file {service}/docker-compose.yaml up -d'"
        )


if __name__ == "__main__":
    if Path(os.getcwd()).name == "ctf_proxy":
        os.chdir("..")
    print("\n")
    services_dict = parse_services()
    edit_services()
    configure_proxy()
    confirmation = input(
        "You are about to restart all your services! Make sure that no catastrophic configuration error has occurred.\nPress Enter to continue"
    )
    restart_services()
