from src.http_parsing import HttpMessageParser

class Stream():
    def __init__(self):
        self.current_data = b""
        self.previous_data = b""
    
    def set_current_data(self, data: bytes):
        pass


class TCPStream(Stream):
    """
    Class for storing TCP data of a single connection.

    current_data: current bytes received (this will be sent to the socket, it can be modified)

    previous_data: entire TCP stream bytes of the connection except current_data
    """
    
    def set_current_data(self, data: bytes):
        self.previous_data = self.current_data
        self.current_data = data

class HTTPStream(Stream):
    """
    Class for storing HTTP data of a single connection.

    current_data: current HTTP request as bytes (this will be sent to the socket, it can be modified)

    previous_data: previous HTTP request as bytes

    current_http: parsed current_data as HttpMessage

    previous_http: parsed previous_data as HttpMessage
    """
    def __init__(self):
        super().__init__()
        self.current_http = None
        self.previous_http = None
    def set_current_data(self, data: bytes):
        self.previous_data = self.current_data
        self.current_data = data
        self.previous_http = self.current_http
        self.current_http = HttpMessageParser(self.current_data).to_message()