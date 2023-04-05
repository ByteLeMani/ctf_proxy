from codecs import decode
import string
from src.http_parsing import HttpRequestParser
class Module():
    def __init__(self):
        pass

    # The attack functions should return a boolean and accept data as a parameter.

    # HTTP examples

    # def curl(self, data: HttpRequestParser):
    #     return "curl" in data.get_headers().get("user-agent")
    
    # def username(self, data: HttpRequestParser):
    #     """
    #     block usernames longer than 10 characters for register endpoint
    #     """
    #     if "register" in data.get_url() and "POST" in data.get_method():
    #         username = data.get_parameters().get("username")
    #         if len(username) > 10:
    #             return True
    #     else:
    #         return False

    # TCP example

    # def nonPrintableChars(self, data: bytes):
    #     return any([chr(c) not in string.printable for c in data])

    def execute(self, data: bytes):
        """
        Returns a string that identifies the attack name.
        If None is returned, no attack has been identified inside data.
        If a string is returned, an attack has been identified and the socket will be closed.
        """
        # data = HttpRequestParser(data)    # uncomment if HTTP
        attacks = []            # [self.username, self.curl]
        for attack in attacks:
            if attack(data):
                return attack.__name__
        return None