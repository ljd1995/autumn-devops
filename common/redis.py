# mypy: disallow-untyped-defs=False
from common.log import Log
import aioredis

from config.setting import settings


class RedisCli(object):
    def __init__(self, *, address: str):
        self._redis_client = None
        self._address = address

    async def init_redis_connect(self) -> None:
        """
        初始化连接
        :return:
        """
        try:
            self._redis_client = await aioredis.from_url(
                url=self._address, decode_responses=True
            )
        except Exception as e:
            Log.exception(f"connect to redis error: {e}")

    # 使实例化后的对象 赋予redis对象的的方法和属性
    def __getattr__(self, name: str):
        return getattr(self._redis_client, name)

    def __getitem__(self, name: str):
        return self._redis_client[name]  # type: ignore

    def __setitem__(self, name: str, value):
        self._redis_client[name] = value  # type: ignore

    def __delitem__(self, name: str):
        del self._redis_client[name]  # type: ignore


# 创建redis连接对象
redis_client = RedisCli(address=settings.REDIS_ADDRESS)

__all__ = ["redis_client"]
