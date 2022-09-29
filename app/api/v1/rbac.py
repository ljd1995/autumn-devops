from app.api.base import BaseRouter
from app.models.rbac import Role, User, Department
from app.schemas.model_creator import RoleReq, DepartmentReq
from app.schemas.rbac import (
    RoleQuerySchema,
    UserQuerySchema,
    UserReqSchema,
    DepartmentQuerySchema,
    RoleRespSchema,
    UserRespSchema,
    DepartmentRespSchema,
    DepartmentChildrenRespSchema,
    DepartmentChildrenQuerySchema,
    UserModifyPasswordReq,
)
from app.schemas.resp import ResponseSchema
from app.services.rbac import DepartmentService, UserService
from common import resp
from fastapi import Response, Depends

role_router = BaseRouter(
    model=Role,
    model_name="角色",
    request_schema=RoleReq,
    response_schema=RoleRespSchema,
    query_schema=RoleQuerySchema,
)

user_router = BaseRouter(
    model=User,
    model_name="用户",
    request_schema=UserReqSchema,
    response_schema=UserRespSchema,
    query_schema=UserQuerySchema,
    page_query_handler=UserService.get_page_queryset,  # type: ignore
)

department_router = BaseRouter(
    model=Department,
    model_name="部门",
    request_schema=DepartmentReq,
    response_schema=DepartmentRespSchema,
    query_schema=DepartmentQuerySchema,
)


@department_router.get("/department/children", response_model=DepartmentChildrenRespSchema, summary="获取部门与子部门关系列表")
async def get_children_data(item: DepartmentChildrenQuerySchema = Depends()) -> Response:
    data = await DepartmentService.get_children_data(item)
    return resp.ok(data=data)


@user_router.post("/user/password", response_model=ResponseSchema, summary="修改用户密码")
async def modify_user_password(item: UserModifyPasswordReq) -> Response:
    await UserService.modify_user_password(item)
    return resp.ok(data="修改用户密码成功")


# 加载CRUD路由一定要在其他路由后面，避免路由冲突
# 详情见 https://fastapi.tiangolo.com/zh/tutorial/path-params/#_7
role_router.load_crud_routes()
user_router.load_crud_routes()
department_router.load_crud_routes()
