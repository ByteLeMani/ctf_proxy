from http_parser.pyparser import HttpParser
import json
from urllib.parse import parse_qsl
from dataclasses import dataclass

@dataclass
class HttpMessage():
    fragment: str
    headers: dict
    method: str
    parameters: dict
    path: str
    query_string: str
    raw_body: bytes
    status_code: int
    url: str
    version: str

class HttpMessageParser(HttpParser):
    def __init__(self, data:bytes, decompress_body=True):
        super().__init__(decompress = decompress_body)
        self.execute(data, len(data))
        self._parameters = {}
        try:
            self._parse_parameters()
        except Exception as e:
            print("Error in parameters parsing:", data)
            print("Exception:", str(e))

    def get_raw_body(self):
        return b"\r\n".join(self._body)
    
    def _parse_query_string(self, raw_string):
        parameters = parse_qsl(raw_string)
        for key,value in parameters:
            try:
                key = key.decode()
                value = value.decode()
            except:
                pass
            if self._parameters.get(key):
                if isinstance(self._parameters[key], list):
                    self._parameters[key].append(value)
                else:
                    self._parameters[key] = [self._parameters[key], value]
            else:
                self._parameters[key] = value

    def _parse_parameters(self):
        if self._method == "POST":
            body = self.get_raw_body()
            if len(body) == 0:
                return
            content_type = self.get_headers().get("Content-Type")
            if not content_type or "x-www-form-urlencoded" in content_type:
                try:
                    self._parse_query_string(body.decode())
                except:
                    pass
            elif "json" in content_type:
                self._parameters = json.loads(body)
        elif self._method == "GET":
            self._parse_query_string(self._query_string)
        
    def get_parameters(self):
        """returns parameters parsed from query string or body"""
        return self._parameters
    
    def get_version(self):
        if self._version:
            return ".".join([str(x) for x in self._version])
        return None

    def to_message(self):
        return HttpMessage(self._fragment, self._headers, self._method,
                           self._parameters, self._path, self._query_string,
                           self.get_raw_body(), self._status_code,
                           self._url, self.get_version()
                           )