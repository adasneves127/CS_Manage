

class UserNotFoundException(Exception):
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)


class MalformedUserException(Exception):
    def __init__(self, message: str = "User data is malformed"):
        self.message = message
        super().__init__(self.message)


class UserNotSignedInException(Exception):
    def __init__(self, message: str = "User not signed in"):
        self.message = message
        super().__init__(self.message)
        
class InvalidPermissionException(Exception):
    def __init__(self, message: str = "User does not have permission to perform this action"):
        self.message = message
        super().__init__(self.message)
        
class MalformedRequestException(Exception):
    def __init__(self, message: str = "Request is malformed"):
        self.message = message
        super().__init__(self.message)