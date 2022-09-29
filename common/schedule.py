# mypy: disallow-untyped-defs=False
from typing import Any

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.setting import settings


class ScheduleCli(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, host: str, port: int):
        self._schedule = None
        self._host = host
        self._port = port

    def init_scheduler(self) -> None:
        """
        初始化 apscheduler
        :return:
        """
        job_stores = {"default": RedisJobStore(host=self._host, port=self._port)}
        self._schedule = AsyncIOScheduler(jobstores=job_stores)
        self._schedule.start()  # type: ignore

    # 使实例化后的对象 赋予apscheduler对象的方法和属性
    def __getattr__(self, name: str):
        return getattr(self._schedule, name)

    def __getitem__(self, name: str):
        return self._schedule[name]  # type: ignore

    def __setitem__(self, name: str, value: Any):
        self._schedule[name] = value  # type: ignore

    def __delitem__(self, name: str):
        del self._schedule[name]  # type: ignore


# 创建schedule对象
schedule = ScheduleCli(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

__all__ = ["schedule"]
