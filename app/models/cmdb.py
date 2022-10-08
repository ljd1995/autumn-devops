from typing import List

from app.models import consts
from app.models.base import BaseModel, DefaultManager
from app.models.enums import HostType, BelongsTo, DiskType, DbType, DbSource, ConfigCenterType
from tortoise import fields


class Host(BaseModel):
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


class Disk(BaseModel):
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


class HostGroup(BaseModel):
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


class Db(BaseModel):
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
        exclude = ["delete_time"]

    def __str__(self) -> str:
        return self.address


class ConfigCenter(BaseModel):
    address = fields.CharField(description="地址", max_length=100)
    port = fields.SmallIntField(description="端口", max_length=10)
    type: ConfigCenterType = fields.CharEnumField(ConfigCenterType, description="类型", default=ConfigCenterType.NACOS)
    version = fields.CharField(description="版本", max_length=30, default="")
    token = fields.CharField(description="访问token", max_length=100, default="")
    remark = fields.CharField(description="备注", max_length=300, default="")

    @classmethod
    def search_fields(cls) -> List[str]:
        return ["address", "version", "remark"]

    class Meta:
        manager = DefaultManager()
        table = "t_config_center"
        table_description = "配置中心表"
        unique_together = ["address", "port"]

    class PydanticMeta:
        exclude = ["delete_time"]

    def __str__(self) -> str:
        return self.address
