# Example
You can test the proxy by copying the contents of the ```example_docker_compose.yml``` file into the proxy ```docker-compose.yml```.

First of all, build and run the proxy. Only after that, build and run the two http services (otherwise the docker network will not be found). 

That's all. You can now enjoy the proxy and see if it works:
```
$ curl localhost
<html><body><h1>It works!</h1></body></html>

$ curl localhost:8080
<html><body><h1>It works!</h1></body></html>
```

## Filtering
In the file http1_in.py from the services modules directory uncomment these lines:
```python
    def SQLi(self, data):
        if "union" in decode(data).lower():
            return True
        else:
            return False
```
and add self.SQLi inside the attacks list:
```python
        attacks = [self.SQLi]
```
We can test if the filter works adding ```union``` anywhere in the request:
```
$ curl localhost/?union
curl: (1) Received HTTP/0.9 when not allowed
```
The proxy answer in case of attacks is not HTTP so curl doesn't understand it. We can analyze the TCP stream inside the .pcap file (if any):
```
GET /?union HTTP/1.1
Host: localhost
User-Agent: curl/7.68.0
Accept: */*

EH! VOLEVI
http1 SQLi
```
![zeb](https://media.tenor.com/RuX0-g3wo-IAAAAC/zeb-zeb89.gif)


This way you can search for attacks on Wireshark by searching for the keyword.