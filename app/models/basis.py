from typing import List

from app.models import consts
from app.models.base import BasicModel, DefaultManager
from app.models.enums import (
    HostType,
    BelongsTo,
    DiskType,
    DbType,
    DbSource,
    ConfigCenterType,
    ApplicationLanguage,
    DeployConfigType,
)
from core.security import get_current_username
from fastapi import Request
from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model
from tortoise.queryset import QuerySetSingle


class Host(BasicModel):
    # 基本信息
    intranet_ip = fields.CharField(description="内网IP", max_length=20, default="")
    external_ip = fields.CharField(description="外网IP", max_length=20, default="")
    host_type: HostType = fields.CharEnumField(
        HostType, description="类型，idc：物理机，cloud：云主机，local：本地虚拟机", default=HostType.LOCAL
    )
    belongs_to: BelongsTo = fields.CharEnumField(BelongsTo, description="服务器归属厂商", default=BelongsTo.LOCAL)
    login_user = fields.CharField(description="用户名", max_length=20, default=consts.SSH_USER)
    password = fields.CharField(description="密码", max_length=60)
    port = fields.SmallIntField(description="SSH端口", default=consts.SSH_PORT)
    remark = fields.CharField(description="备注", max_length=300)
    # 设备信息
    manufacturer = fields.CharField(description="服务器制造商", max_length=50, default="")
    sn = fields.CharField(description="系统序列号", max_length=50, default="")
    uuid = fields.CharField(description="服务器UUID", max_length=50, default="")
    product_name = fields.CharField(description="服务器型号", max_length=50, default="")
    # 系统信息
    distributor = fields.CharField(description="系统厂商", max_length=50, default="")
    release_version = fields.CharField(description="系统版本号", max_length=30, default="")
    kernel_version = fields.CharField(description="内核版本号", max_length=30, default="")
    # CPU信息
    processor_num = fields.SmallIntField(description="逻辑CPU个数", default=0)
    physical_num = fields.SmallIntField(description="物理CPU个数", default=0)
    core_num = fields.SmallIntField(description="每个物理CPU中core的个数(即核数)", default=0)
    # 内存信息
    mem_total = fields.CharField(description="物理内存", max_length=20, default="")
    swap_total = fields.CharField(description="swap缓存", max_length=20, default="")
    # 磁盘信息
    disks: fields.ReverseRelation["Disk"]
    # 网卡信息
    max_bandwidth = fields.SmallIntField(description="网卡最大带宽", default=consts.MAX_BANDWIDTH)
    # 主机组
    host_group: fields.ForeignKeyRelation["HostGroup"] = fields.ForeignKeyField(
        "models.HostGroup", db_constraint=False, related_name="hosts", description="所属主机组"
    )
    proxy_ips = fields.CharField(description="SSH连接代理IP列表", max_length=120, default="")
    env_groups: fields.ManyToManyRelation["EnvironmentGroup"]

    class Meta:
        manager = DefaultManager()
        table = "t_host"
        table_description = "主机信息表"

    class PydanticMeta:
        exclude = ["delete_time", "host_group"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "intranet_ip",
            "external_ip",
            "remark",
            "uuid",
        ]

    def __str__(self) -> str:
        return self.external_ip


class Disk(BasicModel):
    host: fields.ForeignKeyRelation["Host"] = fields.ForeignKeyField(
        "models.Host", db_constraint=False, related_name="disks", description="所属主机"
    )
    name = fields.CharField(description="磁盘名称", max_length=40)
    capacity = fields.CharField(description="磁盘容量", max_length=20)
    interface_type: DiskType = fields.CharEnumField(DiskType, description="接口类型", default=DiskType.HDD)

    class Meta:
        manager = DefaultManager()
        table = "t_disk"
        table_description = "磁盘信息表"

    class PydanticMeta:
        exclude = ["delete_time", "create_time", "update_time", "id"]

    def __str__(self) -> str:
        return self.name


class HostGroup(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    parent: fields.ForeignKeyNullableRelation["HostGroup"] = fields.ForeignKeyField(
        "models.HostGroup",
        db_constraint=False,
        related_name="children",
        description="父级主机组",
        null=True,
    )
    remark = fields.CharField(description="备注", max_length=300, default="")
    children: fields.ReverseRelation["HostGroup"]
    hosts: fields.ReverseRelation["Host"]

    def key(self) -> int:
        return self.id

    def title(self) -> str:
        return self.name

    class Meta:
        manager = DefaultManager()
        table = "t_host_group"
        table_description = "主机组表"
        ordering = ["-id"]

    class PydanticMeta:
        exclude = ["delete_time", "hosts", "parent", "adhoc_historys"]

    def __str__(self) -> str:
        return self.name


class Db(BasicModel):
    address = fields.CharField(description="数据库地址", max_length=100)
    port = fields.SmallIntField(description="数据库端口", max_length=10)
    db_type: DbType = fields.CharEnumField(DbType, description="数据库类型", default=DbType.MYSQL)
    source: DbSource = fields.CharEnumField(DbSource, description="数据库来源", default=DbSource.HOST)
    db_version = fields.CharField(description="数据库版本", max_length=30, default="")
    db_name = fields.CharField(description="数据库名称", max_length=20, default="")
    admin_user = fields.CharField(description="管理员用户名", max_length=30, default="")
    admin_password = fields.CharField(description="管理员密码", max_length=100, default="")
    query_user = fields.CharField(description="仅查询权限用户", max_length=30, default="")
    query_password = fields.CharField(description="仅查询权限用户密码", max_length=100, default="")
    remark = fields.CharField(description="备注", max_length=300, default="")
    db_groups: fields.ReverseRelation["EnvironmentGroup"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "address",
            "db_version",
            "db_name",
            "remark",
        ]

    class Meta:
        manager = DefaultManager()
        table = "t_db"
        table_description = "数据库表"
        unique_together = ["address", "port"]

    class PydanticMeta:
        exclude = ["delete_time", "db_groups"]

    def __str__(self) -> str:
        return self.address


class ConfigCenter(BasicModel):
    address = fields.CharField(description="地址", max_length=100)
    port = fields.SmallIntField(description="端口", max_length=10)
    type: ConfigCenterType = fields.CharEnumField(ConfigCenterType, description="类型", default=ConfigCenterType.NACOS)
    version = fields.CharField(description="版本", max_length=30, default="")
    username = fields.CharField(description="用户名", max_length=30, default="")
    password = fields.CharField(description="密码", max_length=60, default="")
    remark = fields.CharField(description="备注", max_length=300, default="")
    config_groups: fields.ReverseRelation["EnvironmentGroup"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["address", "version", "remark"]

    class Meta:
        manager = DefaultManager()
        table = "t_config_center"
        table_description = "配置中心表"
        unique_together = ["address", "port"]

    class PydanticMeta:
        exclude = ["delete_time", "config_groups"]

    def __str__(self) -> str:
        return self.address


class Application(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    module_name = fields.CharField(description="模块名称", max_length=40, default="")
    service_name = fields.CharField(description="服务名称", max_length=40, default="")
    remark = fields.CharField(description="备注", max_length=300, default="")
    principal = fields.CharField(description="负责人", max_length=50, default="")
    git_url = fields.CharField(description="git地址", max_length=200, default="")
    language: ApplicationLanguage = fields.CharEnumField(
        ApplicationLanguage, description="开发语言", default=ApplicationLanguage.JAVA
    )
    language_version = fields.CharField(description="开发语言版本", max_length=20, default="")
    parameters = fields.CharField(description="启动参数", max_length=100, default="")
    port = fields.CharField(description="启动端口", max_length=10, default="")
    dockerfile_url = fields.CharField(description="dockerfile地址", max_length=100, default="")
    helm_chart_url = fields.CharField(description="helm chart地址", max_length=100, default="")
    git_config: fields.ForeignKeyRelation["DeployConfig"] = fields.ForeignKeyField(
        "models.DeployConfig", db_constraint=False, related_name="applications", description="git配置", null=True
    )
    create_user = fields.CharField(description="创建用户", max_length=30, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")
    application_groups: fields.ReverseRelation["EnvironmentGroup"]

    class Meta:
        manager = DefaultManager()
        table = "t_application"
        table_description = "应用表"

    class PydanticMeta:
        exclude = ["delete_time", "git_config"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    @classmethod
    async def handle_application(cls, application_groups: list, _id: str) -> None:
        for i in application_groups:
            id_ = i.pop("id")
            if id_:
                await EnvironmentGroup.filter(pk=id_).update(
                    name=i.get("name"),
                    remark=i.get("remark"),
                    branch_name=i.get("branch_name"),
                    config_center_ns=i.get("config_center_ns"),
                    k8s_ns=i.get("k8s_ns"),
                    environment_id=i.get("environment").get("id"),
                    db_id=i.get("db").get("id"),
                    config_center_id=i.get("config_center").get("id"),
                    k8s_config_id=i.get("k8s_config_id"),
                    registry_config_id=i.get("registry_config_id"),
                )
                env_group_obj = await EnvironmentGroup.get(pk=id_)
                await env_group_obj.hosts.clear()
                host_instances = [await Host.get(pk=j.get("id")) for j in i.get("hosts")]
                await env_group_obj.hosts.add(*host_instances)
            else:
                env_group_obj = await EnvironmentGroup.create(
                    name=i.get("name"),
                    remark=i.get("remark"),
                    branch_name=i.get("branch_name"),
                    config_center_ns=i.get("config_center_ns"),
                    k8s_ns=i.get("k8s_ns"),
                    environment_id=i.get("environment").get("id"),
                    db_id=i.get("db").get("id"),
                    config_center_id=i.get("config_center").get("id"),
                    k8s_config_id=i.get("k8s_config_id"),
                    registry_config_id=i.get("registry_config_id"),
                    application_id=_id,
                )
                host_instances = [await Host.get(pk=j.get("id")) for j in i.get("hosts")]
                await env_group_obj.hosts.add(*host_instances)

    @classmethod
    async def create_one(cls, item: BaseModel, request: Request) -> Model:
        username = await get_current_username(request)
        items = item.dict(exclude_unset=True)
        application_groups = items.pop("application_groups", [])
        obj = await cls.create(**items, create_user=username)
        await cls.handle_application(application_groups, str(obj.id))
        return obj

    @classmethod
    async def update_one(cls, _id: str, item: BaseModel, request: Request) -> QuerySetSingle[Model]:
        username = await get_current_username(request)
        items = item.dict(exclude_unset=True)
        application_groups = items.pop("application_groups", [])
        await cls.handle_application(application_groups, str(_id))
        await cls.filter(id=_id).update(**items, update_user=username)
        return cls.get(id=_id)  # type: ignore

    def __str__(self) -> str:
        return self.name


class Environment(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    remark = fields.CharField(description="备注", max_length=300, default="")
    environment_groups: fields.ReverseRelation["EnvironmentGroup"]

    class Meta:
        manager = DefaultManager()
        table = "t_environment"
        table_description = "环境表"

    class PydanticMeta:
        exclude = ["delete_time", "environment_groups"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name


class EnvironmentGroup(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    remark = fields.CharField(description="备注", max_length=300, default="")
    branch_name = fields.CharField(description="Git分支名称", max_length=50, default="")
    config_center_ns = fields.CharField(description="配置中心命名空间", max_length=50, default="")
    k8s_ns = fields.CharField(description="K8s集群命名空间", max_length=50, default="")
    environment: fields.ForeignKeyRelation["Environment"] = fields.ForeignKeyField(
        "models.Environment", db_constraint=False, related_name="environment_groups", description="所属环境"
    )
    application: fields.ForeignKeyRelation["Application"] = fields.ForeignKeyField(
        "models.Application", db_constraint=False, related_name="application_groups", description="所属应用"
    )
    db: fields.ForeignKeyRelation["Db"] = fields.ForeignKeyField(
        "models.Db", db_constraint=False, related_name="db_groups", description="使用的数据库"
    )
    config_center: fields.ForeignKeyRelation["ConfigCenter"] = fields.ForeignKeyField(
        "models.ConfigCenter", db_constraint=False, related_name="config_groups", description="使用的配置中心"
    )
    k8s_config: fields.ForeignKeyRelation["DeployConfig"] = fields.ForeignKeyField(
        "models.DeployConfig", db_constraint=False, related_name="k8s_groups", description="k8s配置", null=True
    )
    registry_config: fields.ForeignKeyRelation["DeployConfig"] = fields.ForeignKeyField(
        "models.DeployConfig", db_constraint=False, related_name="registry_groups", description="镜像仓库配置", null=True
    )
    hosts: fields.ManyToManyRelation["Host"] = fields.ManyToManyField(
        "models.Host",
        through="t_env_group_host",
        db_constraint=False,
        related_name="env_groups",
        forward_key="host_id",
        backward_key="env_group_id",
        description="关联主机",
    )
    create_user = fields.CharField(description="创建用户", max_length=30, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")

    class Meta:
        manager = DefaultManager()
        table = "t_env_group"
        table_description = "多环境分组表"

    class PydanticMeta:
        exclude = ["delete_time", "application", "k8s_config", "registry_config"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name


class DeployConfig(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    parameters = fields.JSONField(description="配置参数")
    type: DeployConfigType = fields.CharEnumField(DeployConfigType, description="类型", default=DeployConfigType.K8S)
    remark = fields.CharField(description="备注", max_length=300, default="")

    class Meta:
        manager = DefaultManager()
        table = "t_deploy_config"
        table_description = "部署配置表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name


class ServiceGroup(BasicModel):
    name = fields.CharField(description="名称", max_length=50, unique=True)
    remark = fields.CharField(description="备注", max_length=300, default="")
    create_user = fields.CharField(description="创建用户", max_length=30, default="")
    update_user = fields.CharField(description="更新用户", max_length=30, default="")

    class Meta:
        manager = DefaultManager()
        table = "t_service_group"
        table_description = "服务分组表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["name", "remark"]

    def __str__(self) -> str:
        return self.name
