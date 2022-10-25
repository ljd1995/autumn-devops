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


class CmdExecuteException(APIException):
    status_code_enum = StatusCodeEnum.CMD_EXECUTE_ERROR


class GitOperateException(APIException):
    status_code_enum = StatusCodeEnum.GIT_OPERATE_ERROR


class BuildOperateException(APIException):
    status_code_enum = StatusCodeEnum.BUILD_OPERATE_ERROR


class DockerOperateException(APIException):
    status_code_enum = StatusCodeEnum.DOCKER_OPERATE_ERROR


class HelmOperateException(APIException):
    status_code_enum = StatusCodeEnum.HELM_OPERATE_ERROR


class SqlExecuteException(APIException):
    status_code_enum = StatusCodeEnum.SQL_EXECUTE_ERROR


class ConfigureException(APIException):
    status_code_enum = StatusCodeEnum.CONFIGURE_ERROR


class WebhookException(APIException):
    status_code_enum = StatusCodeEnum.WEBHOOK_ERROR
