#!/usr/bin/python3

import os
import sys
import json
import shutil

from pathlib import Path, PosixPath

import ruamel.yaml  # pip install ruamel.yaml

"""
Why not just use the included yaml package?
Because this one preservs order and comments (and also allows adding them)
"""

blacklist = ["remote_pcap_folder", "caronte", "tulip", "ctf_proxy"]

yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=3, offset=1)

dirs: list[PosixPath] = []
services_dict = {}


class WrongArgument(Exception):
    pass


def parse_dirs():
    """
    If the user provided arguments use them as paths to find the services.
    If not, iterate through the directories and ask for confirmation
    """
    global dirs

    if sys.argv[1:]:
        for dir in sys.argv[1:]:
            d = Path(dir)
            if not d.exists():
                raise WrongArgument(f"The path {dir} doesn't exist")
            if not d.is_dir():
                raise WrongArgument(f"The path {dir} is not a directory")
            dirs.append(d)
    else:
        print(f"No arguments were provided; automatically scanning for services.")
        for file in Path(".").iterdir():
            if file.is_dir() and file.stem[0] != "." and file.stem not in blacklist:
                if "y" in input(f"Is {file.stem} a service? [y/N] "):
                    dirs.append(Path(".", file))


def make_backup():
    global dirs

    for dir in dirs:
        if not Path(dir.name + f"_backup.zip").exists():
            shutil.make_archive(dir.name + f"_backup", "zip", dir)


def parse_services():
    """
    If services.json is present, load it into the global dictionary.
    Otherwise, parse all the docker-compose yamls to build the dictionary and
    then save the result into services.json
    """
    global services_dict, dirs

    for service in dirs:
        file = Path(service, "docker-compose.yml")
        if not file.exists():
            file = Path(service, "docker-compose.yaml")

        with open(file, "r") as fs:
            ymlfile = yaml.load(file)

        services_dict[service.stem] = {"path": str(service.resolve()), "containers": {}}

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
                            f"Is the service {service.stem}:{port[-2]} http? [y/N] "
                        )
                        else False
                    )

                container_dict = {
                    "target_port": [p[-1] for p in ports_list],
                    "listen_port": [p[-2] for p in ports_list],
                    "http": [h for h in http],
                }
                services_dict[service.stem]["containers"][container] = container_dict

            except KeyError:
                print(f"{service.stem}_{container} has no ports binding")
            except Exception as e:
                raise e

        with open("services.json", "w") as backupfile:
            json.dump(services_dict, backupfile, indent=2)
    print("Found services:")
    for service in services_dict:
        print(f"\t{service}")


def edit_services():
    """
    Prepare the docker-compose for each service; comment out the ports, add hostname, add the external network, add an external volume for data persistence (this alone isn't enough - it' s just for convenience since we are already here)
    """
    global services_dict

    for service in services_dict:
        file = Path(services_dict[service]["path"], "docker-compose.yml")
        if not file.exists():
            file = Path(services_dict[service]["path"], "docker-compose.yaml")

        with open(file, "r") as fs:
            ymlfile = yaml.load(file)

        for container in services_dict[service]["containers"]:
            try:
                # Add a comment with the ports
                target_ports = services_dict[service]["containers"][container][
                    "target_port"
                ]
                listen_ports = services_dict[service]["containers"][container][
                    "listen_port"
                ]
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
                if "hostname" in ymlfile["services"][container]:
                    print(
                        f"[!] Error: service {service}_{container} already has a hostname. Skipping this step, review it manually before restarting."
                    )
                else:
                    ymlfile["services"][container]["hostname"] = hostname

            except Exception as e:
                json.dump(ymlfile, sys.stdout, indent=2)
                print(f"\n{container = }")
                raise e

            # TODO: Add restart: always

            # add external network
            net = {"default": {"name": "ctf_network", "external": True}}
            if "networks" in ymlfile:
                if "default" not in ymlfile["networks"]:
                    ymlfile["networks"].append(net)
                else:
                    print(
                        f"[!] Error: service {service} already has a default network. Skipping this step, review it manually before restarting."
                    )
            else:
                ymlfile["networks"] = net

            # write file
            with open(file, "w") as fs:
                yaml.dump(ymlfile, fs)


def configure_proxy():
    """
    Properly configure both the proxy's docker-compose with the listening ports and the config.json with all the services.
    We can't automatically configure ssl for now, so it's better to set https services as not http so they keep working at least. Manually configure the SSL later and turn http back on.
    """
    # Download ctf_proxy
    if not Path("./ctf_proxy").exists():
        os.system("git clone https://github.com/ByteLeMani/ctf_proxy.git")

    with open("./ctf_proxy/docker-compose.yml", "r") as file:
        ymlfile = yaml.load(file)

    # Add all the ports to the compose
    ports = []
    for service in services_dict:
        for container in services_dict[service]["containers"]:
            for port in services_dict[service]["containers"][container]["listen_port"]:
                ports.append(f"{port}:{port}")
    # ymlfile["services"]["proxy"]["ports"] = ports
    ymlfile["services"]["nginx"]["ports"] = ports
    with open("./ctf_proxy/docker-compose.yml", "w") as fs:
        yaml.dump(ymlfile, fs)

    # Proxy config.json
    print("Remember to manually edit the config for SSL")
    services = []
    for service in services_dict:
        for container in services_dict[service]["containers"]:
            name = f"{service}_{container}"
            target_ports = services_dict[service]["containers"][container][
                "target_port"
            ]
            listen_ports = services_dict[service]["containers"][container][
                "listen_port"
            ]
            http = services_dict[service]["containers"][container]["http"]
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
    """
    Make sure every service is off and then start them one by one after the proxy
    """

    for service in services_dict:
        os.system(
            f"bash -c '!(docker compose --file {services_dict[service]['path']}/docker-compose.yml down) && docker compose --file {services_dict[service]['path']}/docker-compose.yaml down'"
        )

    os.system(
        f"bash -c 'docker compose --file ctf_proxy/docker-compose.yml restart; docker compose --file ctf_proxy/docker-compose.yml up -d'"
    )

    for service in services_dict:
        os.system(
            f"bash -c '!(docker compose --file {services_dict[service]['path']}/docker-compose.yml up -d) && docker compose --file {services_dict[service]['path']}/docker-compose.yaml up -d'"
        )


def main():
    global services_dict

    if Path(os.getcwd()).name == "ctf_proxy":
        os.chdir("..")

    if Path("./services.json").exists():
        print("Found existing services file")
        with open("./services.json", "r") as fs:
            services_dict = json.load(fs)

    if "RESTART" in sys.argv:
        if not services_dict:
            print(
                f"Can't restart without first parsing the services. Please run the script at least once without the RESTART flag"
            )
        else:
            restart_services()
        return

    parse_dirs()
    parse_services()
    make_backup()

    edit_services()
    configure_proxy()
    confirmation = input(
        "You are about to restart all your services! Make sure that no catastrophic configuration error has occurred.\nPress Enter to continue"
    )
    restart_services()


if __name__ == "__main__":
    main()
