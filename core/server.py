from glob import glob
from importlib import import_module
from inspect import getmembers
from pathlib import Path
from typing import List

from common.error_handler import error_handlers
from common.middlewares import AuditMiddleware
from common.redis import redis_client
from common.schedule import schedule
from tasks import rearq_obj
from config import db
from config.setting import settings
from fastapi import FastAPI, APIRouter
from rearq.server.app import app as rearq_app
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from tortoise import Tortoise, connections


def create_app() -> FastAPI:
    """
    生成FatAPI对象
    :return:
    """
    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        openapi_url=settings.OPENAPI_URL,
        redoc_url=settings.REDOC_URL,
        exception_handlers=error_handlers,  # type: ignore
    )

    # 跨域设置
    register_cors(app)

    # 注册路由
    register_router(app)

    # 注册中间件
    register_middleware(app)

    # 注册任务队列
    register_rearq(app)

    # 注册事件监听
    register_event(app)

    return app


def register_router(app: FastAPI) -> None:
    """
    注册路由
    :param app:
    :return:
    """
    routers: List = []
    module_name: str = "app.api.v1"
    base = Path(__file__).parent.parent
    for path in glob(f"{base}/app/api/v1/*.py", recursive=True):
        file_name = path.split("/")[-1].split(".")[0]
        module = import_module(f"{module_name}.{file_name}", app.__module__)
        for _, member in getmembers(module):
            if isinstance(member, APIRouter):
                routers.append(member)
    for router in routers:
        if router.tags:
            tags = router.tags
        else:
            tags = [str(router)]
        app.include_router(router, prefix=settings.API_V1_STR, tags=tags)
    # 挂载static file
    app.mount(f"{settings.API_V1_STR}/uploads", StaticFiles(directory="uploads"), name="uploads")


def register_cors(app: FastAPI) -> None:
    """
    支持跨域
    :param app:
    :return:
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_middleware(app: FastAPI) -> None:
    """
    注册中间件
    :param app:
    :return:
    """
    app.add_middleware(AuditMiddleware)


def register_event(app: FastAPI) -> None:
    """
    注册事件监听
    :param app:
    :return:
    """

    @app.on_event("startup")
    async def init_connect() -> None:
        # 初始化ORM
        await Tortoise.init(config=db.TORTOISE_ORM)
        # 挂载关系数据库连接对象到上下文
        app.state.db = connections.get("default")

        # 连接redis
        await redis_client.init_redis_connect()

        # 初始化rearq
        await rearq_obj.init()

        # 初始化 apscheduler
        schedule.init_scheduler()

    @app.on_event("shutdown")
    async def shutdown_connect() -> None:
        # 关闭 ORM 连接
        await connections.close_all()

        # 关闭rearq
        await rearq_obj.close()

        # 关闭schedule
        schedule.shutdown()


def register_rearq(app: FastAPI) -> None:
    """
    注册rearq任务队列
    :param app:
    :return:
    """
    app.mount("/rearq", rearq_app)
    rearq_app.set_rearq(rearq_obj)
