from http import HTTPStatus


class HTTPException(Exception):
    def __init__(self, status_code: HTTPStatus, detail: str):
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        return f"ERROR: {self.status_code}, {self.detail}"


class NotFound(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail)


class BadRequest(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "internal server error"):
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail)
