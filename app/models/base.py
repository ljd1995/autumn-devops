from datetime import datetime
from typing import Dict, List

from app.models.enums import Status
from pydantic import BaseModel as ModelBase
from tortoise import models, fields
from tortoise.expressions import Q
from tortoise.manager import Manager
from tortoise.models import MODEL
from tortoise.queryset import QuerySet, QuerySetSingle

from fastapi import Request


class DefaultManager(Manager):
    """
    默认 ORM Manager，默认 queryset不包含逻辑删除的数据
    """

    def get_queryset(self) -> QuerySet[MODEL]:
        return super(DefaultManager, self).get_queryset().filter(delete_time=None).order_by("-id")


class BaseModel(models.Model):
    id = fields.IntField(description="主键ID", pk=True)
    create_time = fields.DatetimeField(description="创建时间", auto_now_add=True)
    update_time = fields.DatetimeField(description="更新时间", auto_now=True)
    delete_time = fields.DatetimeField(description="删除时间", null=True, default=None)

    @classmethod
    def _construct_orm_filter(
        cls, field_name: str, search_value: str | int, lookup_sep: str = "__", lookup_suffix: str = "icontains"
    ) -> Dict[str, str | int]:
        orm_lookup = lookup_sep.join([field_name, lookup_suffix])
        return {orm_lookup: search_value}

    @classmethod
    def fuzzy_search(cls, *, search_fields: List[str] | None = None, search_value: str) -> QuerySet[MODEL]:
        if search_fields is None:
            search_fields = cls.search_fields()
        if search_value:
            orm_filter = [Q(**cls._construct_orm_filter(search_field, search_value)) for search_field in search_fields]
            return cls.filter(Q(*orm_filter, join_type=Q.OR))
        return cls.all()

    @classmethod
    def search_fields(cls) -> List[str]:
        return []

    @classmethod
    async def create_one(cls, item: ModelBase, request: Request) -> MODEL:
        return await cls.create(**item.dict())

    @classmethod
    async def find_by(cls, **kwargs) -> list[ModelBase]:  # type: ignore
        return await cls.filter(**kwargs)

    @classmethod
    async def find_one(cls, **kwargs) -> ModelBase | None:  # type: ignore
        return await cls.filter(**kwargs).first()

    @classmethod
    async def update_one(cls, _id: str, item: ModelBase, request: Request) -> QuerySetSingle[MODEL]:
        await cls.filter(id=_id).update(**item.dict(exclude_unset=True))
        return cls.get(id=_id)

    @classmethod
    async def delete_one(cls, _id: str, request: Request) -> int:
        deleted_count = await cls.filter(id=_id).update(delete_time=datetime.now())
        return deleted_count

    class Meta:
        abstract = True


class ModelWithStatus(BaseModel):
    status: Status = fields.IntEnumField(Status, description="状态，0：启用，1：禁用", default=Status.ENABLE)

    class Meta:
        abstract = True
