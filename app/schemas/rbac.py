from typing import List

from app.models.enums import Status
from app.schemas.paginate import BasePageSchema
from app.schemas.resp import ResponseSchema
from pydantic import Field, BaseModel
from .model_creator import UserModel, DepartmentModel, RoleModel, UserReq


class UserRespSchema(ResponseSchema):
    result: UserModel | None  # type: ignore


class DepartmentRespSchema(ResponseSchema):
    result: DepartmentModel | None  # type: ignore


class DepartmentChildrenRespSchema(ResponseSchema):
    result: List[DepartmentModel] | None  # type: ignore


class RoleRespSchema(ResponseSchema):
    result: RoleModel | None  # type: ignore


class UserReqSchema(UserReq):
    password: str | None = None


class UserQuerySchema(BasePageSchema):
    department_id: int | str | None = Field(default=None, description="所属部门ID")
    status: Status | None = Field(default=None, description="0:启用, 1:禁用")


class RoleQuerySchema(BasePageSchema):
    status: Status | None = Field(default=None, description="0:启用, 1:禁用")


class DepartmentQuerySchema(BasePageSchema):
    status: Status | None = Field(default=None, description="0:启用, 1:禁用")


class DepartmentChildrenQuerySchema(BaseModel):
    search: str | int | None = None
    status: Status | None = Field(default=None, description="0:启用, 1:禁用")


class UserModifyPasswordReq(BaseModel):
    username: str
    password_old: str
    password_new: str
