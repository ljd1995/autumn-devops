from app.schemas.paginate import BasePageSchema
from app.schemas.resp import ResponseSchema
from pydantic import Field
from .model_creator import OperatorAuditRecordModel, SSHAuditRecordModel


class OperatorAuditRecordRespSchema(ResponseSchema):
    result: OperatorAuditRecordModel | None  # type: ignore


class OperatorAuditRecordQuerySchema(BasePageSchema):
    username: str | None = Field(default=None, description="用户名")


class SSHAuditRecordRespSchema(ResponseSchema):
    result: SSHAuditRecordModel | None  # type: ignore


class SSHAuditRecordQuerySchema(BasePageSchema):
    username: str | None = Field(default=None, description="用户名")
