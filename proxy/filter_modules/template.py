from src.stream import Stream, TCPStream, HTTPStream
# from src.db_manager import DBManager

class Module():
    
    # INFO: uncomment these functions to enable them

    # HTTP Example
    
    # def username(self, stream: HTTPStream):
    #     """
    #     block usernames longer than 10 characters for register endpoint
    #     """
    #     message = stream.current_http_message
    #     if "register" in message.url and "POST" in message.method:
    #         username = message.parameters.get("username")
    #         if len(username) > 10:
    #             return True
    #     else:
    #         return False

    # TCP Example

    # def password(self, stream: TCPStream):
    #     """block passwords longer than 10 characters"""
    #     if b"Insert password:" in stream.previous_messages[0] and len(stream.current_message.strip()) > 10:
    #         return True
    #     return False

    # other examples are in the example_functions.py file

    def execute(self, stream: Stream):
        """
        Returns a string that identifies the attack name.
        If None is returned, no attack has been identified inside data.
        If a string is returned, an attack has been identified and the socket will be closed.
        """
        
        ignored_functions = [] # ["password"]
        
        attacks = [getattr(Module, attribute) for attribute in dir(Module) if callable(getattr(Module, attribute)) and attribute.startswith('__') is False and attribute != "execute" and attribute not in ignored_functions]

        for attack in attacks:
            try:
                if attack(self, stream):
                    return attack.__name__
            except IndexError:
                pass
        return None