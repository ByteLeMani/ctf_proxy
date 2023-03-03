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
        Returns two values, data and the attack name.
        If data is None, the socket gets closed.
        If data is not None, the content of data will be forwarded to the target ip.
        If an attack is found, its name (attack.__name__) and packet content will be saved into the db.
        """
        attacks = []            # [self.SQLi, self.XSS]
        for attack in attacks:
            if attack(data):
                return attack.__name__
        return None