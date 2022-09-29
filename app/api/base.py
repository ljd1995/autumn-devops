import re
from typing import Type, Callable, Dict

from app.models.base import BaseModel
from app.models.paginate import Pagination
from app.schemas.paginate import BasePageSchema
from common import resp
from core.security import check_token
from fastapi import APIRouter, status, Depends, Response, Request
from pydantic import BaseModel as ModelBase
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import MODEL
from tortoise.queryset import QuerySet


class BaseRouter(APIRouter):
    def __init__(
        self,
        *,
        request_schema: Type[ModelBase],
        response_schema: Type[ModelBase],
        query_schema: Type[BasePageSchema],
        model: Type[BaseModel],
        model_name: str,
        page_query_handler: Callable[
            [QuerySet[MODEL], Dict],
            QuerySet[MODEL],
        ] = None,
        model_path: str | None = None,
        tag_name: str | None = None,
    ):
        super().__init__(dependencies=[Depends(check_token)])
        self._request_schema = request_schema
        self._response_schema = response_schema
        self._query_schema = query_schema
        self._model = model
        self._model_name = model_name
        self._page_query_handler = page_query_handler
        self._model_path = model_path
        self._tag_name = tag_name

    def load_crud_routes(
        self,
        only_paginate: bool = False,
        exclude_paginate: bool = False,
    ) -> None:
        request_schema: Type[ModelBase] = self._request_schema
        response_schema = self._response_schema
        query_schema: Type[BasePageSchema] = self._query_schema
        model = self._model
        if self._model_path:
            model_path = self._model_path
        else:
            model_path = re.sub("(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])", "-\\g<0>", model.__name__).lower()
        model_name = self._model_name
        page_query_handler = self._page_query_handler
        pydantic_model = pydantic_model_creator(model)
        if not exclude_paginate:

            @self.get(
                "/" + model_path,
                response_model=response_schema,
                summary=f"列出所有{model_name}",
            )
            async def fetch_all(item: query_schema = Depends()) -> Response:  # type: ignore
                query = item.dict(exclude_unset=True, exclude_none=True)  # type: ignore
                page = query.pop("page")
                page_size = query.pop("page_size")
                search_value = query.pop("search", None)

                queryset = model.fuzzy_search(search_value=search_value)
                if query:
                    if page_query_handler:
                        queryset = await page_query_handler(queryset, query)
                    else:
                        queryset = queryset.filter(**query)

                p = Pagination(page, page_size)  # type: ignore
                ret = await p.paginate_queryset(queryset)
                result = await pydantic_model.from_queryset(ret)
                data = p.get_paginated_result(result)

                return resp.ok(data=data)

        if not only_paginate:

            @self.get(
                "/" + model_path + "/{item_id}",
                response_model=response_schema,
                summary=f"根据id获取{model_name}详情",
            )
            async def fetch_one(item_id: str) -> Response:
                data = await pydantic_model.from_queryset_single(model.get(id=item_id))
                return resp.ok(data=data)

            @self.post(
                "/" + model_path,
                status_code=status.HTTP_201_CREATED,
                response_model=response_schema,
                summary=f"创建{model_name}",
            )
            async def create(item: request_schema, request: Request) -> Response:  # type: ignore
                new_item = await model.create_one(item, request)
                data = await pydantic_model.from_tortoise_orm(new_item)
                return resp.ok(
                    data=data,
                    status_code=status.HTTP_201_CREATED,
                )

            @self.put(
                "/" + model_path + "/{item_id}",
                response_model=response_schema,
                summary=f"更新{model_name}信息",
            )
            async def update(item_id: str, item: request_schema, request: Request) -> Response:  # type: ignore
                updated_item = await model.update_one(item_id, item, request)
                data = await pydantic_model.from_queryset_single(updated_item)
                return resp.ok(data=data)

            @self.delete("/" + model_path + "/{item_id}", summary=f"删除{model_name}")
            async def delete(item_id: str, request: Request) -> Response:
                await model.delete_one(item_id, request)
                return resp.ok(data=None)

    def __str__(self) -> str:
        if self._tag_name:
            return self._tag_name
        return self._model_name
