from app.api.base import BaseRouter
from app.models.basis import Host, HostGroup, Db, ConfigCenter, Application, Environment, EnvironmentGroup, DeployConfig
from app.schemas.basis import (
    HostRespSchema,
    HostGroupRespSchema,
    HostQuerySchema,
    HostGroupQuerySchema,
    HostGroupChildrenRespSchema,
    AssociateHostGroupReq,
    DbRespSchema,
    DbQuerySchema,
    GetDbSchemaReq,
    GetDbTableReq,
    GetDbColumnReq,
    DbExecuteSqlReq,
    ConfigCenterRespSchema,
    ConfigCenterQuerySchema,
    ApplicationRespSchema,
    ApplicationQuerySchema,
    EnvironmentGroupRespSchema,
    EnvironmentGroupQuerySchema,
    EnvironmentQuerySchema,
    EnvironmentRespSchema,
    ApplicationReq,
    DeployConfigRespSchema,
    DeployConfigQuerySchema,
)
from app.schemas.model_creator import (
    HostReq,
    HostGroupReq,
    DbReq,
    ConfigCenterReq,
    EnvironmentGroupReq,
    EnvironmentReq,
    DeployConfigReq,
)
from app.schemas.resp import ResponseSchema
from app.services.basis import HostGroupService, HostService, DbService
from common import resp
from fastapi import Response

host_router = BaseRouter(
    model=Host,
    model_name="主机",
    tag_name="CMDB",
    model_path="cmdb/host",
    request_schema=HostReq,
    response_schema=HostRespSchema,
    query_schema=HostQuerySchema,
    page_query_handler=HostService.get_page_queryset,  # type: ignore
)

host_group_router = BaseRouter(
    model=HostGroup,
    model_name="主机组",
    tag_name="CMDB",
    model_path="cmdb/host-group",
    request_schema=HostGroupReq,
    response_schema=HostGroupRespSchema,
    query_schema=HostGroupQuerySchema,
)

db_router = BaseRouter(
    model=Db,
    model_name="数据库",
    tag_name="CMDB",
    model_path="cmdb/db",
    request_schema=DbReq,
    response_schema=DbRespSchema,
    query_schema=DbQuerySchema,
)

config_center_router = BaseRouter(
    model=ConfigCenter,
    model_name="配置中心",
    tag_name="CMDB",
    model_path="cmdb/config-center",
    request_schema=ConfigCenterReq,
    response_schema=ConfigCenterRespSchema,
    query_schema=ConfigCenterQuerySchema,
)

application_router = BaseRouter(
    model=Application,
    model_name="应用",
    tag_name="应用配置",
    model_path="app/application",
    request_schema=ApplicationReq,
    response_schema=ApplicationRespSchema,
    query_schema=ApplicationQuerySchema,
)
environment_router = BaseRouter(
    model=Environment,
    model_name="环境",
    tag_name="应用配置",
    model_path="app/environment",
    request_schema=EnvironmentReq,
    response_schema=EnvironmentRespSchema,
    query_schema=EnvironmentQuerySchema,
)
environment_group_router = BaseRouter(
    model=EnvironmentGroup,
    model_name="环境组",
    tag_name="应用配置",
    model_path="app/env-group",
    request_schema=EnvironmentGroupReq,
    response_schema=EnvironmentGroupRespSchema,
    query_schema=EnvironmentGroupQuerySchema,
)

deploy_config_router = BaseRouter(
    model=DeployConfig,
    model_name="部署配置",
    tag_name="CMDB",
    request_schema=DeployConfigReq,
    response_schema=DeployConfigRespSchema,
    query_schema=DeployConfigQuerySchema,
    model_path="cmdb/deploy-config",
)


@host_group_router.get(
    "/cmdb/host-group/children", response_model=HostGroupChildrenRespSchema, summary="获取主机组与子主机组关系列表"
)
async def get_children_data() -> Response:
    data = await HostGroupService.get_children_data()
    return resp.ok(data=data)


@host_group_router.get(
    "/cmdb/host-group/children-host", response_model=HostGroupChildrenRespSchema, summary="获取主机组与子主机组关系列表,并关联主机"
)
async def get_children_data_with_host() -> Response:
    data = await HostGroupService.get_children_data_with_host()
    return resp.ok(data=data)


@host_router.post("/cmdb/host/host-group", response_model=ResponseSchema, summary="关联主机组")
async def associate_host_group(item: AssociateHostGroupReq) -> Response:
    await HostService.associate_host_group(item)
    return resp.ok(data="更新主机组成功")


@db_router.post("/cmdb/db/schema", response_model=ResponseSchema, summary="获取数据库管理系统中所有数据库名")
async def get_schema_names(item: GetDbSchemaReq) -> Response:
    data = await DbService.get_schema_names(item)
    return resp.ok(data=data)


@db_router.post("/cmdb/db/table", response_model=ResponseSchema, summary="获取某个数据库中所有表信息")
async def get_table_info(item: GetDbTableReq) -> Response:
    data = await DbService.get_table_info(item)
    return resp.ok(data=data)


@db_router.post("/cmdb/db/column", response_model=ResponseSchema, summary="获取数据库中某个表所有字段信息")
async def get_columns(item: GetDbColumnReq) -> Response:
    data = await DbService.get_columns(item)
    return resp.ok(data=data)


@db_router.post("/cmdb/db/sql", response_model=ResponseSchema, summary="在某个数据库执行SQL")
async def execute_sql(item: DbExecuteSqlReq) -> Response:
    data = await DbService.execute_sql(item)
    return resp.ok(data=data)


# 加载CRUD路由一定要在其他路由后面，避免路由冲突
# 详情见 https://fastapi.tiangolo.com/zh/tutorial/path-params/#_7
host_router.load_crud_routes()
host_group_router.load_crud_routes()
db_router.load_crud_routes()
config_center_router.load_crud_routes()
application_router.load_crud_routes()
environment_router.load_crud_routes()
environment_group_router.load_crud_routes()
deploy_config_router.load_crud_routes()
