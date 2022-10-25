from typing import List

from app.models.base import DefaultManager, BasicModel
from core.security import get_current_username
from fastapi import Request
from pydantic import BaseModel
from tortoise import fields, models
from tortoise.models import MODEL
from tortoise.queryset import QuerySetSingle
from utils.crypt import md5_encode
from .basis import HostGroup
from .enums import ExecCommand, ScriptType


class AdhocHistory(BasicModel):
    username = fields.CharField(description="用户名", max_length=20, default="")
    host_group: fields.ForeignKeyRelation["HostGroup"] = fields.ForeignKeyField(
        "models.HostGroup", db_constraint=False, related_name="adhoc_historys", description="所属主机组"
    )
    host_pattern = fields.CharField(description="限制", max_length=100, default="")
    module = fields.CharField(description="模块", max_length=50)
    module_args = fields.CharField(description="模块参数", max_length=200, default="")
    fork = fields.SmallIntField(description="并发")

    class Meta:
        manager = DefaultManager()
        table = "t_adhoc_history"
        table_description = "adhoc执行历史表"
        ordering = ["-id"]

    class PydanticMeta:
        exclude = [
            "delete_time",
            "update_time",
        ]

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "username",
            "host_pattern",
            "module",
            "module_args",
        ]

    def __str__(self) -> str:
        return self.module


class Script(BasicModel):
    name = fields.CharField(description="脚本名称", max_length=30, default="")
    content = fields.TextField(description="脚本内容", null=True, default="")
    exec_command: ExecCommand = fields.CharEnumField(ExecCommand, description="脚本执行程序", default=ExecCommand.SHELL)
    remark = fields.CharField(description="备注", max_length=300, default="")
    node_type: ScriptType = fields.CharEnumField(ScriptType, description="节点类型", default=ScriptType.NODE)
    create_user = fields.CharField(description="创建用户", max_length=30, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")
    parent: fields.ForeignKeyNullableRelation["Script"] = fields.ForeignKeyField(
        "models.Script",
        db_constraint=False,
        related_name="children",
        description="父级脚本组",
        null=True,
    )

    def key(self) -> int:
        return self.id

    def title(self) -> str:
        return self.name

    @classmethod
    async def create_one(cls, item: BaseModel, request: Request) -> MODEL:
        username = await get_current_username(request)
        return await cls.create(**item.dict(), create_user=username)  # type: ignore

    @classmethod
    async def update_one(cls, _id: str, item: BaseModel, request: Request) -> QuerySetSingle[MODEL]:
        username = await get_current_username(request)
        obj = await cls.get(id=_id)
        new_content_md5 = md5_encode(item.content)  # type: ignore
        # 记录脚本更新历史
        await ScriptHistory.create(
            script_id=_id,
            old_content=obj.content,
            new_content=item.content,  # type: ignore
            update_user=username,
            md5=new_content_md5,
        )
        # 更新脚本
        await cls.filter(id=_id).update(**item.dict(exclude_unset=True), update_user=username)
        return cls.get(id=_id)  # type: ignore

    class Meta:
        manager = DefaultManager()
        table = "t_script"
        table_description = "脚本表"

    class PydanticMeta:
        exclude = ["delete_time", "parent", "script_history"]

    def __str__(self) -> str:
        return self.name


class ScriptHistory(models.Model):
    id = fields.IntField(description="主键ID", pk=True)
    script: fields.ForeignKeyRelation["Script"] = fields.ForeignKeyField(
        "models.Script",
        db_constraint=False,
        related_name="script_history",
        description="所属脚本",
    )
    old_content = fields.TextField(description="旧脚本内容", null=True, default="")
    new_content = fields.TextField(description="新脚本内容", null=True, default="")
    md5 = fields.CharField(description="MD5", max_length=50, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")
    update_time = fields.DatetimeField(description="更新时间", auto_now_add=True)

    class Meta:
        table = "t_script_history"
        table_description = "脚本历史表"
        ordering = ["-id"]

    class PydanticMeta:
        exclude = ["script"]

    def __str__(self) -> str:
        return self.md5
