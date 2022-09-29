from fastapi.exceptions import RequestValidationError

from common import resp
from common.code_msg import StatusCodeEnum
from common.log import Log
from fastapi import Request, Response


async def all_exception_handler(request: Request, exception: Exception) -> Response:
    # 自定义异常，获取异常定义的 status_code 属性
    status_code_enum = getattr(exception, "status_code_enum", None)
    exception_name = type(exception).__name__

    if status_code_enum is None:
        match exception_name:
            case "ValidationError" | "TypeError" | "RequestValidationError":
                status_code_enum = StatusCodeEnum.PARAMETER_VALIDATE_ERROR
            case "IntegrityError":
                status_code_enum = StatusCodeEnum.INTEGRITY_ERROR
            case "AttributeError":
                status_code_enum = StatusCodeEnum.ATTRIBUTE_ERROR
            case "DoesNotExist":
                status_code_enum = StatusCodeEnum.NOT_EXIST_ERROR
            case "NotFound":
                status_code_enum = StatusCodeEnum.NOT_FOUND_ERROR
            case "AuthenticationFailed":
                status_code_enum = StatusCodeEnum.AUTHENTICATION_FAILED_ERROR
            case "Unauthorized":
                status_code_enum = StatusCodeEnum.UNAUTHORIZED_ERROR
            case "OperationalError":
                status_code_enum = StatusCodeEnum.OPERATIONAL_ERROR
            case _:
                status_code_enum = StatusCodeEnum.ERROR

    # 打印异常，如果异常没捕获，输出到日志，后续根据日志进行捕获
    if status_code_enum == StatusCodeEnum.ERROR:
        Log.error(f"this exception is not catch, type: {exception_name},message：{str(exception)}")
    else:
        Log.error(f"{request.method} {request.url} happened exception, type: {exception_name},message：{str(exception)}")

    # 输出详细异常追溯信息，方便日常问题定位
    Log.exception(exception)

    return resp.fail(status_enum=status_code_enum, exception_detail=str(exception))


error_handlers = {
    Exception: all_exception_handler,
    RequestValidationError: all_exception_handler,
}
