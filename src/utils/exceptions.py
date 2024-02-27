

class UserNotFoundException(Exception):
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)
        
class MalformedUserException(Exception):
    def __init__(self, message: str = "User data is malformed"):
        self.message = message
        super().__init__(self.message)