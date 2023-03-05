# ctf_proxy - A TCP proxy for intercepting and dropping malicious attacks

This tool is purposely made for Attack/Defence CTF competitions. It opens as many listening socket as there are services, receives packets to be analyzed by custom filters that drop or forward them towards the services, opening a remote socket to them.

## Usage
The tool can be used as a Docker container or as a CLI Python application.
It requires some initialization parameters:

- **TARGET_IPS**: the hostnames or IPs of each service
- **TARGET_PORTS**: the ports of each service
- **LISTEN_PORTS**: ports to listen on for each service
- **KEYWORD**: Keyword to use as a response for malicious packets to quickly find them in a pcap file

### Docker Example
Clone the repository:
```
git clone https://github.com/ByteLeMani/ctf_proxy
cd ctf_proxy
```
Edit the docker-compose.yml file with the parameters for your needs and run the container:
```
docker-compose up --build -d
```
#### FOR A/D CONTAINERIZED SERVICES
You can add this configuration to the services docker-compose.yml file and remove any address/port binding it may have, to take advantage of the docker network DNS.
```
networks:
  default:
    name: ctf_network
    external: true
```
This way, you can use the services name in TARGET_IPS parameter. Moreover, as the services are connected to the proxy network they are reachable inside the network without exposing or changing any port, but not reachable from the outside.
### CLI Example
Clone the repository and install the required packages:
```bash
git clone https://github.com/ByteLeMani/ctf_proxy
cd ./ctf_proxy/proxy
pip install -r requirements.txt
```
Then edit the following command and run the script for your needs:
```bash
python3 proxy.py --target-ips example_ip [example_ip ...] \
  --target-ports example_port [example_port ...] \
  --listen-ports example_port [example_port ...] \
  --keyword example_keyword
```

## Modules
These are the core filtering entities of the proxy. For each proxied service, a pair of modules is generated inside the ```proxy/proxymodules/services``` folder. Modules execution will follow this flow: 

![proxy](https://user-images.githubusercontent.com/93737876/222970657-3ebb5253-3587-4a84-8f0d-6c6381d91016.jpg)

Inside the modules you will find an ```execute``` method that receives data from the proxy and returns to the proxy whether the data contains an attack or not. If an attack is found, the proxy will send to the attacker a custom string (```KEYWORD + "\n" + TARGET_IP + ATTACK NAME``` to easily find attacks in PCAP files if a packet analyzer is used in the system) and then the socket will be closed.
### Update module
To add a new filter, define a new function inside the class Module called as the name of the attack (or a custom one if you prefer) that accepts data as parameter and returns a boolean (True if attack found, False if not). Then add it to the attacks list inside the execute method to enable it. You will find a filter example inside the template.

Every module will be ***automatically reloaded on the fly*** by simply modifying it. If an exception is thrown during the import, the module will not be loaded and the previous version will be used instead. If an exception is thrown at runtime, the packet will simply flow through the proxy.

## Logging
A simple log file called ```log.txt``` inside the ```proxy``` directory will count all the blocked packets for each service. If the file already exists at startup, the proxy will update the counts based on their initial value inside the file. Otherwise, the file will be created at startup.

You can monitor the file by using:
```
watch cat log.txt
```
Any relevant information will be printed to stdout. Set ```VERBOSE``` to ```true``` for more info.

If you're using the Docker version, you can inspect the docker logs to access them: 
```
docker logs --follow proxy
```
## Credits
Written by:
- [fcirillo00](https://github.com/fcirillo00)
- [AleDecre](https://github.com/AleDecre)

This tool is inspired by and partially based on the TCP proxy logic of [tcpproxy.py](https://github.com/ickerwx/tcpproxy/blob/master/tcpproxy.py).