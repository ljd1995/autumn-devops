from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    # 开发模式配置
    DEBUG: bool = False

    # API版本
    API_V1_STR: str = "/api/v1"
    # 项目文档
    TITLE: str = "Autumn-DevOps"
    DESCRIPTION: str = (
        "autumn is a devops solution based on Python FastAPI, dedicated to providing devops management"
        " platform support for small and medium enterprises."
    )
    # 文档地址 默认为docs 生产环境关闭 None
    DOCS_URL: str = "/api/v1/docs"
    # 文档关联请求数据接口
    OPENAPI_URL: str = "/api/v1/openapi.json"
    # redoc 文档
    REDOC_URL: Optional[str] = "/api/v1/redoc"

    # access token过期时间
    ACCESS_TOKEN_EXPIRE_DELTA: int = 60 * 60 * 12

    # refresh token过期时间
    REFRESH_TOKEN_EXPIRE_DELTA: int = 60 * 60 * 24

    # 生成token的加密算法
    ALGORITHM: str = "HS256"

    # 生产环境保管好 SECRET_KEY
    SECRET_KEY: str = "$0VyKlQ.eFdDg8zbeIyk2IO"

    # AES KEY
    AES_KEY: str = "gY@y]);HI2ZS2dZj(T5(M;_~K%^gS.r6"

    # AES IV
    AES_IV: str = "akUrcXyP9u/VezJi"

    # 数据库地址
    DB_ADDRESS: str = "mysql://root:123456@127.0.0.1:3306/autumn"

    # Redis Host
    REDIS_HOST: str = "127.0.0.1"
    # Redis Port
    REDIS_PORT: int = 6379
    # Redis database
    REDIS_DB: int = 0
    # Redis地址
    REDIS_ADDRESS: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # SSH 连接超时
    SSH_CONNECT_TIMEOUT: int = 5
    # SSH是否统一走代理
    SSH_UNIT_PROXY: bool = False
    # SSH统一走代理时默认代理主机IP
    SSH_UNIT_PROXY_IP: str = ""
    # SFTP上传的目的目录
    SFTP_UPLOAD_DIR: str = "/tmp"


settings = Settings()
