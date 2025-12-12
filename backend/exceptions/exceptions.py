class GenerateException(Exception):
    """Generate Error"""

    def __init__(self, message: str, endpoint: str, status_code: int | None = None):
        self.message: str = message
        self.endpoint: str = endpoint
        self.status_code: int | None = status_code
        super().__init__(message)


class PublishException(Exception):
    """Publish Error"""

    def __init__(self, message: str, endpoint: str, status_code: int | None = None):
        self.message: str = message
        self.endpoint: str = endpoint
        self.status_code: int | None = status_code
        super().__init__(message)


class UntitleException(Exception):
    """Untitled Exception"""

    def __init__(self, message: str, endpoint: str, status_code: int | None = None):
        self.message: str = message
        self.endpoint: str = endpoint
        self.status_code: int | None = status_code
        super().__init__(message)


class SessionException(Exception):
    """Session Exception"""

    def __init__(self, message: str, endpoint: str, status_code: int | None = None):
        self._message: str = message
        self._endpoint: str = endpoint
        self._status_code: int | None = status_code
        super().__init__(message)
