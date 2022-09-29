from app.api.base import BaseRouter
from app.models.job import AdhocHistory, Script
from app.schemas.job import (
    AdhocHistoryQuerySchema,
    AdhocHistoryRespSchema,
    ExecModuleReq,
    ScriptRespSchema,
    ScriptQuerySchema,
    ScriptChildRenRespSchema,
    ScriptOptionRespSchema,
    ExecTaskReq,
)
from app.schemas.model_creator import AdhocHistoryReq, ScriptReq
from app.schemas.resp import ResponseSchema
from app.services.job import JobService
from common import resp
from core.security import get_current_username
from fastapi import Response, Depends

job_router = BaseRouter(
    model=AdhocHistory,
    tag_name="作业平台",
    model_name="Adhoc操作历史",
    request_schema=AdhocHistoryReq,
    response_schema=AdhocHistoryRespSchema,
    query_schema=AdhocHistoryQuerySchema,
    model_path="job/adhoc-history",
)

script_router = BaseRouter(
    model=Script,
    tag_name="作业平台",
    model_name="脚本",
    request_schema=ScriptReq,
    response_schema=ScriptRespSchema,
    query_schema=ScriptQuerySchema,
    model_path="job/script",
)


@job_router.post("/job/module", response_model=ResponseSchema, summary="执行远程模块")
async def exec_module(item: ExecModuleReq, username: str = Depends(get_current_username)) -> Response:
    data = await JobService.exec_module(item, username)
    return resp.ok(data=data)


@job_router.post("/job/task", response_model=ResponseSchema, summary="执行远程任务")
async def exec_task(item: ExecTaskReq) -> Response:
    data = await JobService.exec_task(item)
    return resp.ok(data=data)


@script_router.get("/job/script/children", response_model=ScriptChildRenRespSchema, summary="获取脚本组与子脚本关系列表")
async def get_children_data() -> Response:
    data = await JobService.get_children_data()
    return resp.ok(data=data)


@script_router.get("/job/script/history/{item_id}", response_model=ScriptChildRenRespSchema, summary="获取脚本更新历史")
async def get_script_history(item_id: int) -> Response:
    data = await JobService.get_script_history(item_id)
    return resp.ok(data=data)


@script_router.get("/job/script/options", response_model=ScriptOptionRespSchema, summary="获取所有脚本options")
async def get_all_script_options() -> Response:
    data = await JobService.get_all_script_options()
    return resp.ok(data=data)


job_router.load_crud_routes(
    only_paginate=True,
)

script_router.load_crud_routes(
    exclude_paginate=True,
)
