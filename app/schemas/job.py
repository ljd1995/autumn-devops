from typing import List

from app.schemas.paginate import BasePageSchema
from app.schemas.resp import ResponseSchema
from pydantic import BaseModel, Field
from .model_creator import AdhocHistoryModel, ScriptModel


class ExecModuleReq(BaseModel):
    host_group_id: int
    module: str
    module_args: str | None
    host_pattern: str | None = Field(default="*", description="限制")
    fork: int | None = Field(default=10, description="并发")


class ExecTaskReq(BaseModel):
    host_group_id: int
    host_pattern: str
    content: str
    exec_command: str


class AdhocHistoryRespSchema(ResponseSchema):
    result: AdhocHistoryModel | None  # type: ignore


class AdhocHistoryQuerySchema(BasePageSchema):
    username: str | None = Field(default=None, description="用户名")


class ScriptRespSchema(ResponseSchema):
    result: ScriptModel | None  # type: ignore


class ScriptQuerySchema(BasePageSchema):
    ...


class ScriptChildRenRespSchema(ResponseSchema):
    result: ScriptModel | None  # type: ignore


class ScriptOptionItem(BaseModel):
    label: str
    value: str


class ScriptOptionSchema(BaseModel):
    label: str
    options: List[ScriptOptionItem]


class ScriptOptionRespSchema(ResponseSchema):
    result: List[ScriptOptionSchema] | None
