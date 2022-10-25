from typing import List

from app.models.base import BasicModel, DefaultManager
from tortoise import fields
from .basis import Application, Environment


class Artifact(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    remark = fields.CharField(description="备注", max_length=300, default="")
    create_user = fields.CharField(description="创建用户", max_length=30, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")
    pipelines: fields.ReverseRelation["Pipeline"]

    class Meta:
        manager = DefaultManager()
        table = "t_artifact"
        table_description = "制品表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name


class Pipeline(BasicModel):
    name = fields.CharField(description="名称", max_length=50)
    job_id = fields.CharField(description="事务ID", max_length=50, unique=True)
    remark = fields.CharField(description="备注", max_length=300, default="")
    environment: fields.ForeignKeyRelation["Environment"] = fields.ForeignKeyField(
        "models.Environment", db_constraint=False, related_name="env_pipelines", description="所属环境"
    )
    artifact: fields.ForeignKeyRelation["Artifact"] = fields.ForeignKeyField(
        "models.Artifact", db_constraint=False, related_name="pipelines", description="所属制品"
    )
    application: fields.ForeignKeyRelation["Application"] = fields.ForeignKeyField(
        "models.Application", db_constraint=False, related_name="app_pipelines", description="所属应用"
    )
    create_user = fields.CharField(description="创建用户", max_length=30, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")
    pipeline_plugins: fields.ReverseRelation["PipelinePlugin"]

    class Meta:
        manager = DefaultManager()
        table = "t_pipeline"
        table_description = "流水线表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name


class PipelinePlugin(BasicModel):
    name = fields.CharField(description="名称", max_length=50)
    parameters = fields.JSONField(description="配置参数")
    order = fields.SmallIntField(description="配置参数", default=0)
    pipeline: fields.ForeignKeyRelation["Pipeline"] = fields.ForeignKeyField(
        "models.Pipeline", db_constraint=False, related_name="pipeline_plugins", description="所属流水线"
    )

    class Meta:
        manager = DefaultManager()
        table = "t_pipeline_plugin"
        table_description = "流水线插件表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name


class CICDPlugin(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    default_parameters = fields.JSONField(description="配置参数")
    remark = fields.CharField(description="备注", max_length=300, default="")

    class Meta:
        manager = DefaultManager()
        table = "t_cicd_plugin"
        table_description = "CICD插件表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name
