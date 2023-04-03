from http_parser.pyparser import HttpParser
import json
from urllib.parse import parse_qsl

class HttpRequestParser(HttpParser):
    def __init__(self, data:bytes, decompress_body=True):
        super().__init__(decompress = decompress_body)
        self.execute(data, len(data))
        self._parameters = {}
        self._parse_parameters()

    def get_raw_body(self):
        return b"".join(self._body)
    
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
            if not content_type:
                return
            if "x-www-form-urlencoded" in content_type:
                self._parse_query_string(body)
            elif "json" in content_type:
                self._parameters = json.loads(body)
        elif self._method == "GET":
            self._parse_query_string(self._query_string)
        
    def get_parameters(self):
        return self._parameters