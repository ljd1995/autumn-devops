from enum import Enum
from fastapi import status


class StatusCodeEnum(Enum):
    """状态码枚举类"""

    # base
    OK = (0, "成功", status.HTTP_200_OK)
    ERROR = (-1, "发生错误", status.HTTP_400_BAD_REQUEST)

    # ORM相关
    INTEGRITY_ERROR = (10001, "数据库异常", status.HTTP_422_UNPROCESSABLE_ENTITY)
    NOT_EXIST_ERROR = (10002, "数据不存在", status.HTTP_404_NOT_FOUND)
    OPERATIONAL_ERROR = (10003, "数据库操作失败", status.HTTP_400_BAD_REQUEST)

    # 程序相关
    ATTRIBUTE_ERROR = (20001, "属性错误", status.HTTP_422_UNPROCESSABLE_ENTITY)
    PARAMETER_VALIDATE_ERROR = (20002, "参数校验失败", status.HTTP_422_UNPROCESSABLE_ENTITY)
    INVALID_USAGE_ERROR = (20003, "未验证的参数", status.HTTP_400_BAD_REQUEST)
    NOT_FOUND_ERROR = (20004, "URL路径不存在", status.HTTP_404_NOT_FOUND)
    REDIS_OPERATE_ERROR = (20005, "redis操作异常", status.HTTP_400_BAD_REQUEST)
    AUTHENTICATION_FAILED_ERROR = (20006, "token认证失败", status.HTTP_403_FORBIDDEN)
    TOKEN_EXPIRED_ERROR = (20007, "token过期", status.HTTP_403_FORBIDDEN)
    UNAUTHORIZED_ERROR = (20008, "未登录或未验证的用户名密码", status.HTTP_401_UNAUTHORIZED)
    TOKEN_TIMEOUT_ERROR = (20009, "登录超时", status.HTTP_403_FORBIDDEN)
    SSH_ERROR = (20010, "SSH连接异常", status.HTTP_400_BAD_REQUEST)

    # 系统运行相关
    SERVICE_UNAVAILABLE_ERROR = (30001, "服务不可用", status.HTTP_400_BAD_REQUEST)
    CANCELLED_ERROR = (30002, "异步任务被动取消", status.HTTP_400_BAD_REQUEST)
    TIMEOUT_ERROR = (30003, "系统超时", status.HTTP_400_BAD_REQUEST)

    @property
    def code(self) -> int:
        """获取状态码"""
        return self.value[0]

    @property
    def message(self) -> str:
        """获取状态码信息"""
        return self.value[1]

    @property
    def status(self) -> int:
        """获取http响应码信息"""
        return self.value[2]
