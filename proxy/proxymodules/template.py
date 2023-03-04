from codecs import decode

class Module():
    def __init__(self):
        pass

    # The attack functions should return a boolean and accept data as a parameter.

    # def XSS(self, data):
    #     if "<script>" in decode(data).lower():
    #         return True
    #     else:
    #         return False

    # def SQLi(self, data):
    #     if "union" in decode(data).lower():
    #         return True
    #     else:
    #         return False
    
    def execute(self, data):
        """
        Returns a string that identifies the attack name.
        If None is returned, no attack has been identified inside data.
        If a string is returned, an attack has been identified and the socket will be closed.
        """
        attacks = []            # [self.SQLi, self.XSS]
        for attack in attacks:
            if attack(data):
                return attack.__name__
        return None