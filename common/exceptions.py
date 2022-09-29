from common.code_msg import StatusCodeEnum


class APIException(Exception):
    status_code_enum: StatusCodeEnum = StatusCodeEnum.ERROR

    def __init__(self, error_info: str):
        super().__init__(self)
        self.error_info = error_info

    def __str__(self) -> str:
        return self.error_info


class RedisException(APIException):
    status_code_enum = StatusCodeEnum.REDIS_OPERATE_ERROR


class TokenTimeoutException(APIException):
    status_code_enum = StatusCodeEnum.TOKEN_TIMEOUT_ERROR


class UnauthorisedException(APIException):
    status_code_enum = StatusCodeEnum.UNAUTHORIZED_ERROR


class AuthenticationFailedException(APIException):
    status_code_enum = StatusCodeEnum.AUTHENTICATION_FAILED_ERROR


class SSHOperatorException(APIException):
    status_code_enum = StatusCodeEnum.SSH_ERROR
