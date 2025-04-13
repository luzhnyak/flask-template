from flask import jsonify
from werkzeug.exceptions import HTTPException
from http import HTTPStatus as status


class APIException(HTTPException):
    def __init__(
        self, detail="An error occurred", status_code=status.INTERNAL_SERVER_ERROR
    ):
        self.response = jsonify({"error": detail})
        self.response.status_code = status_code


class NotFoundException(APIException):
    def __init__(self, detail="Resource not found"):
        super().__init__(detail, status.NOT_FOUND)


class ConflictException(APIException):
    def __init__(self, detail="Conflict occurred"):
        super().__init__(detail, status.CONFLICT)


class ForbiddenException(APIException):
    def __init__(self, detail="Forbidden"):
        super().__init__(detail, status.FORBIDDEN)


class BadRequestException(APIException):
    def __init__(self, detail="Bad request"):
        super().__init__(detail, status.BAD_REQUEST)


class UnauthorizedException(APIException):
    def __init__(self, detail="Unauthorized"):
        super().__init__(detail, status.UNAUTHORIZED)


class ValidationException(APIException):
    def __init__(self, detail="Invalid data"):
        super().__init__(detail, status.UNPROCESSABLE_ENTITY)


class DatabaseException(APIException):
    def __init__(self, detail="Database error"):
        super().__init__(f"Database error: {detail}", status.INTERNAL_SERVER_ERROR)


class ServerException(APIException):
    def __init__(self, detail="Server error"):
        super().__init__(f"Server error: {detail}", status.INTERNAL_SERVER_ERROR)
