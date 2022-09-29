import asyncio
from typing import Callable, Any


async def run_async(func: Callable, /, *args, **kwargs) -> Any:  # type: ignore
    """
    在不同的线程中异步地运行阻塞函数 func, 返回执行结果。
    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    result = await asyncio.to_thread(func, *args, **kwargs)
    return result
