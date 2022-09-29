from typing import List

from app.schemas.paginate import BasePageSchema
from app.schemas.resp import ResponseSchema
from pydantic import Field, BaseModel
from .model_creator import HostModel, HostGroupModel, DbModel
from ..models.enums import HostType, BelongsTo, DbType, DbSource


class HostRespSchema(ResponseSchema):
    result: HostModel | None  # type: ignore


class HostGroupRespSchema(ResponseSchema):
    result: HostGroupModel | None  # type: ignore


class DbRespSchema(ResponseSchema):
    result: DbModel | None  # type: ignore


class HostGroupChildrenRespSchema(ResponseSchema):
    result: List[HostGroupModel] | None  # type: ignore


class HostQuerySchema(BasePageSchema):
    host_group_id: int | str | None = Field(default=None, description="所属主机组ID")
    host_type: HostType | None = Field(default=None, description="idc: 物理机, cloud:云主机, local:本地虚拟机")
    belongs_to: BelongsTo | None = Field(default=None)


class HostGroupQuerySchema(BasePageSchema):
    ...


class DbQuerySchema(BasePageSchema):
    db_type: DbType | None = Field(default=None)
    source: DbSource | None = Field(default=None)


class AssociateHostGroupReq(BaseModel):
    host_group_id: int | str
    host_ids: List[int]


class GetDbSchemaReq(BaseModel):
    username: str
    password: str
    host: str
    port: int
    db_type: str


class GetDbTableReq(GetDbSchemaReq):
    schema_name: str = Field(description="数据库名")


class GetDbColumnReq(GetDbTableReq):
    table_name: str = Field(description="表名")


class DbExecuteSqlReq(GetDbTableReq):
    sql: str = Field(description="查询SQL")
