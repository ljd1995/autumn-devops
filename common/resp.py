import datetime
from datetime import timedelta

from app.schemas.resp import ResponseSchema, TypeEnum
from common.code_msg import StatusCodeEnum
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel


def ok(
    status_enum: StatusCodeEnum = StatusCodeEnum.OK,
    *,
    data: list | dict | str | PydanticModel | BaseModel | None = None,
    status_code: int | None = None,
) -> Response:
    _status = status.HTTP_200_OK
    if status_code:
        _status = status_code
    else:
        _status = status_enum.status
    return ORJSONResponse(
        status_code=_status,
        content=jsonable_encoder(
            ResponseSchema(
                code=status_enum.code,
                message=status_enum.message,
                result=data,
                type=TypeEnum.SUCCESS,
            ),
            custom_encoder={
                datetime.datetime: lambda date_obj: (date_obj + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            },
        ),
    )


def fail(*, status_enum: StatusCodeEnum, exception_detail: str) -> Response:
    return ORJSONResponse(
        status_code=status_enum.status,
        content=jsonable_encoder(
            ResponseSchema(
                code=status_enum.code,
                message=status_enum.message + "," + exception_detail,
                result=None,
                type=TypeEnum.ERROR,
            )
        ),
    )
