from typing import Dict, List

from pydantic import BaseModel


class BasePageSchema(BaseModel):
    page: int | None = 1
    page_size: int | None = 10
    search: str | int | None = None


class PaginationSchema(BaseModel):
    page: int
    page_size: int
    total_pages: int
    total_count: int
    items: Dict | List | None
