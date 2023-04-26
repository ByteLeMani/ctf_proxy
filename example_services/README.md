# Example
First of all, build and run the proxy. The provided `config.json` file is already suited to the example. 

Only after that, build and run the two http services (otherwise the docker network will not be found). 

That's all. You can now enjoy the proxy and see if it works:
```
$ curl http://localhost
<html><body><h1>It works!</h1></body></html>

$ curl https://localhost
<html><body><h1>It works!</h1></body></html>
```

## Filtering
In the file `http_service_in.py`, from the `filter_modules/http_service` directory, add this function:
```python
    def SQLi(self, stream: HTTPStream):
        return "union" in stream.current_http_message.query_string
```
We can test if the filter works adding `union` in the query string.
Let's run a TCP capture using `tcpdump`:
```bash
sudo tcpdump -s 0 -i lo port 80 or port 443 -w mycap.pcap
```
Then let's try to attack our service:
```
$ curl localhost/?union
curl: (1) Received HTTP/0.9 when not allowed
```
The proxy answer in this case is not HTTP but purely TCP so `curl` doesn't understand it.
If we look inside the .pcap file we've just generated, we can easily find the attack by searching for the keyword `EH! VOLEVI`:

```
GET /?union HTTP/1.1
Host: localhost
User-Agent: curl/7.68.0
Accept: */*

EH! VOLEVI http_service SQLi
```
![zeb](https://media.tenor.com/RuX0-g3wo-IAAAAC/zeb-zeb89.gif)

It also works on TLS encrypted communications, because the keyword will be sent as plaintext.