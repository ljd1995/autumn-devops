from app.api.base import BaseRouter
from app.models.wiki import WikiZone, WikiCategory, WikiPage
from app.schemas.model_creator import WikiZoneReq, WikiCategoryReq, WikiPageReq
from app.schemas.resp import ResponseSchema
from app.schemas.wiki import (
    WikiZoneRespSchema,
    WikiZoneQuerySchema,
    WikiCategoryQuerySchema,
    WikiCategoryRespSchema,
    WikiCategoryChildrenRespSchema,
    WikiPageRespSchema,
    WikiPageQuerySchema,
    WikiCategoryPageQuerySchema,
)
from app.services.wiki import WikiCategoryService, WikiPageService
from common import resp
from fastapi import Response, Depends, UploadFile

zone_router = BaseRouter(
    model=WikiZone,
    tag_name="Wiki",
    model_name="wiki空间",
    request_schema=WikiZoneReq,
    response_schema=WikiZoneRespSchema,
    query_schema=WikiZoneQuerySchema,
    model_path="wiki/zone",
)

category_router = BaseRouter(
    model=WikiCategory,
    tag_name="Wiki",
    model_name="wiki目录",
    request_schema=WikiCategoryReq,
    response_schema=WikiCategoryRespSchema,
    query_schema=WikiCategoryQuerySchema,
    model_path="wiki/category",
)

page_router = BaseRouter(
    model=WikiPage,
    tag_name="Wiki",
    model_name="wiki页面",
    request_schema=WikiPageReq,
    response_schema=WikiPageRespSchema,
    query_schema=WikiPageQuerySchema,
    model_path="wiki/page",
)


@category_router.get(
    "/wiki/children-page", response_model=WikiCategoryChildrenRespSchema, summary="获取wiki目录与子目录关系列表,并关联wiki页面"
)
async def get_children_data_with_page(item: WikiCategoryPageQuerySchema = Depends()) -> Response:
    data = await WikiCategoryService.get_children_data_with_page(item)
    return resp.ok(data=data)


@page_router.post("/wiki/page/file", response_model=ResponseSchema, summary="wiki页面上传文件")
async def handle_upload_file(file: UploadFile) -> Response:
    url = await WikiPageService.upload_file(file)
    return resp.ok(data=url)


zone_router.load_crud_routes()
category_router.load_crud_routes(exclude_paginate=True)
page_router.load_crud_routes(exclude_paginate=True)
