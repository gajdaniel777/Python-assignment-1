class SubLedgerError(Exception):
    """Base domain error."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(SubLedgerError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ConflictError(SubLedgerError):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)
