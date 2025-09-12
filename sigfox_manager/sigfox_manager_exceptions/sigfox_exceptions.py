class SigfoxAPIException(Exception):
    def __init__(
        self,
        status_code,
        message="Error occurred while fetching contracts from Sigfox API",
    ):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Status Code: {self.status_code})"


class SigfoxAuthError(SigfoxAPIException):
    def __init__(self, message="User Not authorized to access the resource"):
        super().__init__(401, message)


class SigfoxDeviceNotFoundError(SigfoxAPIException):
    def __init__(self, message="Device not found"):
        super().__init__(404, message)


class SigfoxDeviceCreateConflictException(SigfoxAPIException):
    def __init__(
        selfself, message="A conflict happened with the current state of the resource."
    ):
        super().__init__(409, message)
