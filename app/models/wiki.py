from app.models.base import BaseModel, DefaultManager
from core.security import get_current_username
from fastapi import Request
from pydantic import BaseModel as ModelBase
from tortoise import fields
from tortoise.models import MODEL
from tortoise.queryset import QuerySetSingle


class WikiPage(BaseModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    content = fields.TextField(description="内容", default="")
    secret = fields.CharField(description="访问密钥", max_length=50, default="")
    create_user = fields.CharField(description="创建人", max_length=30, default="")
    update_user = fields.CharField(description="更新人", max_length=30, default="")
    remark = fields.CharField(description="备注", max_length=300, default="")
    wiki_category: fields.ForeignKeyRelation["WikiCategory"] = fields.ForeignKeyField(
        "models.WikiCategory", db_constraint=False, related_name="pages", description="所属wiki目录"
    )

    class Meta:
        manager = DefaultManager()
        table = "t_wiki_page"
        table_description = "wiki页面表"

    class PydanticMeta:
        exclude = ["delete_time", "wiki_category", "page_history"]

    @classmethod
    async def create_one(cls, item: ModelBase, request: Request) -> MODEL:
        username = await get_current_username(request)
        return await cls.create(**item.dict(), create_user=username)

    @classmethod
    async def update_one(cls, _id: str, item: ModelBase, request: Request) -> QuerySetSingle[MODEL]:
        username = await get_current_username(request)
        await cls.filter(id=_id).update(**item.dict(exclude_unset=True), update_user=username)
        return cls.get(id=_id)

    def __str__(self) -> str:
        return self.name


class WikiZone(BaseModel):
    name = fields.CharField(description="空间名称", max_length=50, unique=True)
    cover_image_url = fields.CharField(description="封面图片地址", max_length=200, default="")
    create_user = fields.CharField(description="创建人", max_length=30, default="")
    remark = fields.CharField(description="备注", max_length=300, default="")
    categories: fields.ReverseRelation["WikiCategory"]

    class Meta:
        manager = DefaultManager()
        table = "t_wiki_zone"
        table_description = "wiki空间表"

    class PydanticMeta:
        exclude = ["delete_time", "categories"]

    @classmethod
    async def create_one(cls, item: ModelBase, request: Request) -> MODEL:
        username = await get_current_username(request)
        return await cls.create(**item.dict(), create_user=username)

    def __str__(self) -> str:
        return self.name


class WikiCategory(BaseModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    parent: fields.ForeignKeyNullableRelation["WikiCategory"] = fields.ForeignKeyField(
        "models.WikiCategory",
        db_constraint=False,
        related_name="children",
        description="父目录",
        null=True,
    )
    zone: fields.ForeignKeyNullableRelation["WikiZone"] = fields.ForeignKeyField(
        "models.WikiZone",
        db_constraint=False,
        related_name="categories",
        description="所属空间",
        null=True,
    )
    remark = fields.CharField(description="备注", max_length=300, default="")
    children: fields.ReverseRelation["WikiCategory"]
    pages: fields.ReverseRelation["WikiPage"]

    def key(self) -> int:
        return self.id

    def title(self) -> str:
        return self.name

    class Meta:
        manager = DefaultManager()
        table = "t_wiki_category"
        table_description = "wiki目录表"

    class PydanticMeta:
        exclude = ["delete_time", "parent", "zone", "pages"]

    def __str__(self) -> str:
        return self.name
