from math import ceil

from app.schemas.paginate import PaginationSchema
from tortoise.contrib.pydantic import PydanticModel
from tortoise.queryset import QuerySet


class Pagination(object):
    max_page_size: int = 500

    def __init__(self, page: int = 1, page_size: int = 10) -> None:
        self._page: int = page
        self._page_size: int = page_size
        self._total_count: int = 0
        self._total_pages: int = 0
        if self._page_size > self.max_page_size:
            self._page_size = self.max_page_size

    @staticmethod
    async def _get_total_count(queryset: QuerySet) -> int:
        return await queryset.count()

    async def _get_total_pages(self) -> int:
        return ceil(self._total_count / self._page_size)

    @property
    async def total_count(self) -> int:
        return self._total_count

    @property
    async def total_pages(self) -> int:
        return self._total_pages

    async def paginate_queryset(self, queryset: QuerySet) -> QuerySet:
        """Return queryset"""
        self._total_count = await self._get_total_count(queryset)
        self._total_pages = await self._get_total_pages()
        offset = (self._page - 1) * self._page_size
        return queryset.limit(self._page_size).offset(offset)

    def get_paginated_result(
        self, data: list[PydanticModel] | None
    ) -> PaginationSchema | None:
        if data:
            return PaginationSchema(
                page=self._page,
                page_size=self._page_size,
                total_count=self._total_count,
                total_pages=self._total_pages,
                items=data,
            )
        return None
