from typing import List

from app.models import consts
from app.models.base import BasicModel, DefaultManager
from app.models.enums import HttpMethod, SSHStatus
from tortoise import fields


class OperatorAuditRecord(BasicModel):
    username = fields.CharField(description="用户名", max_length=50)
    request_url = fields.CharField(description="请求URL", max_length=400)
    request_method: HttpMethod = fields.CharEnumField(HttpMethod, description="请求方法", default=HttpMethod.POST)
    request_body = fields.TextField(description="请求参数", default="")
    response_code = fields.SmallIntField(description="响应码", default=consts.RESPONSE_CODE)
    response_content = fields.TextField(
        description="响应内容",
        default="",
    )
    request_time = fields.DatetimeField(description="请求时间", auto_now_add=True)
    process_time = fields.FloatField(description="耗时时间")

    class Meta:
        manager = DefaultManager()
        table = "t_operator_audit"
        table_description = "操作审计表"
        ordering = ["-id"]

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "username",
            "request_url",
            "request_method",
            "request_body",
            "response_code",
            "response_content",
        ]

    def __str__(self) -> str:
        return (
            f"{self.username} request {self.request_url} in {self.request_time},request method is {self.request_method}"
        )


class SSHAuditRecord(BasicModel):
    username = fields.CharField(description="用户名", max_length=50)
    ssh_host = fields.CharField(description="SSH主机", max_length=20)
    ssh_user = fields.CharField(description="SSH用户名", max_length=20)
    proxy_host = fields.CharField(description="SSH使用的代理主机", max_length=20, default="")
    status: SSHStatus = fields.IntEnumField(SSHStatus, description="在线状态", default=SSHStatus.OFFLINE)
    ssh_command = fields.TextField(description="历史操作命令", default="")

    class Meta:
        manager = DefaultManager()
        table = "t_ssh_audit"
        table_description = "SSH操作审计表"

    class PydanticMeta:
        exclude = ["delete_time"]

    @classmethod
    def search_fields(cls) -> List[str]:
        return [
            "username",
            "ssh_host",
            "ssh_user",
            "ssh_command",
        ]

    def __str__(self) -> str:
        return f"{self.username} command {self.ssh_command}"
