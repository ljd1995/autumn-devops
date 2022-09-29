from typing import List

from app.schemas.paginate import BasePageSchema
from app.schemas.resp import ResponseSchema
from pydantic import BaseModel
from .model_creator import WikiZoneModel, WikiCategoryModel, WikiPageModel


class WikiZoneRespSchema(ResponseSchema):
    result: WikiZoneModel | None  # type: ignore


class WikiZoneQuerySchema(BasePageSchema):
    ...


class WikiCategoryRespSchema(ResponseSchema):
    result: WikiCategoryModel | None  # type: ignore


class WikiCategoryQuerySchema(BasePageSchema):
    ...


class WikiPageRespSchema(ResponseSchema):
    result: WikiPageModel | None  # type: ignore


class WikiPageQuerySchema(BasePageSchema):
    ...


class WikiCategoryChildrenRespSchema(ResponseSchema):
    result: List[WikiCategoryModel] | None  # type: ignore


class WikiCategoryPageQuerySchema(BaseModel):
    zone_id: str | int


class WikiSharePageQuerySchema(BaseModel):
    page_id: str | int
