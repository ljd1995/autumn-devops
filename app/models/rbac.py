from typing import List

from app.models.base import ModelWithStatus, DefaultManager
from common.exceptions import APIException
from fastapi import Request
from passlib.context import CryptContext
from pydantic import BaseModel
from tortoise import fields
from tortoise.models import MODEL
from tortoise.queryset import QuerySetSingle

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(ModelWithStatus):
    username = fields.CharField(description="用户名", max_length=20, unique=True)
    password = fields.CharField(description="登录密码", max_length=80)
    nick_name = fields.CharField(description="用户昵称", max_length=50, default="")
    phone = fields.CharField(description="手机号", max_length=20, default="")
    email = fields.CharField(description="邮箱", max_length=30, default="")
    qq = fields.CharField(description="qq号", max_length=20, default="")
    avatar = fields.CharField(description="头像", max_length=100, default="")
    introduction = fields.TextField(description="详细介绍", default="")
    last_login_time = fields.DatetimeField(description="上次登陆时间", auto_now=True, default=None)
    last_login_ip = fields.CharField(description="上次登陆IP", max_length=30, default="")
    department: fields.ForeignKeyNullableRelation["Department"] = fields.ForeignKeyField(
        "models.Department",
        db_constraint=False,
        related_name="users",
        description="所属部门",
        null=True,
    )
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role",
        through="user_role",
        db_constraint=False,
        related_name="users",
        forward_key="role_id",
        backward_key="user_id",
        description="关联角色",
    )

    class Meta:
        manager = DefaultManager()
        table = "t_user"
        table_description = "用户信息表"

    class PydanticMeta:
        exclude = ["delete_time", "password", "roles", "department"]

    @classmethod
    async def find_by_id(cls, _id: int | str) -> MODEL:
        return await cls.filter(pk=_id).first()  # type: ignore

    @staticmethod
    def generate_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_hash(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    @classmethod
    async def create_one(cls, item: BaseModel, request: Request) -> MODEL:
        if hasattr(item, "password"):
            if item.password:  # type: ignore
                item.password = cls.generate_hash(item.password)  # type: ignore
            else:
                raise APIException("password can not be empty")
        return await cls.create(**item.dict())  # type: ignore

    @classmethod
    async def update_one(cls, _id: str, item: BaseModel, request: Request) -> QuerySetSingle[MODEL]:
        if hasattr(item, "password") and item.password is not None:  # type: ignore
            item.password = cls.generate_hash(item.password)  # type: ignore
        await cls.filter(id=_id).update(**item.dict(exclude_unset=True))
        return cls.get(id=_id)  # type: ignore

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "username",
            "nick_name",
            "introduction",
            "phone",
            "email",
        ]

    def __str__(self) -> str:
        return self.username


class Department(ModelWithStatus):
    name = fields.CharField(description="部门名称", max_length=40)
    code = fields.CharField(description="部门标识", max_length=80)
    parent: fields.ForeignKeyNullableRelation["Department"] = fields.ForeignKeyField(
        "models.Department",
        db_constraint=False,
        related_name="children",
        description="父级部门",
        null=True,
    )
    remark = fields.CharField(description="备注", max_length=300, default="")
    children: fields.ReverseRelation["Department"]

    class Meta:
        manager = DefaultManager()
        table = "t_department"
        table_description = "部门信息表"
        unique_together = ("name", "code")

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "name",
            "code",
            "remark",
        ]

    class PydanticMeta:
        exclude = ("delete_time", "parent", "children", "users")

    def __str__(self) -> str:
        return self.name


class Role(ModelWithStatus):
    name = fields.CharField(description="角色名称", max_length=40)
    code = fields.CharField(description="角色标识", max_length=80)
    remark = fields.CharField(description="备注", max_length=300, default="")
    users: fields.ManyToManyRelation["User"]

    class Meta:
        manager = DefaultManager()
        table = "t_role"
        table_description = "角色信息表"
        unique_together = ("name", "code")

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "name",
            "code",
            "remark",
        ]

    class PydanticMeta:
        exclude = ("delete_time", "users")

    def __str__(self) -> str:
        return self.name
