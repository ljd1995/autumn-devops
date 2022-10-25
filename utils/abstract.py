import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict

import aiofiles
from common.log import Log


class DbOperator(ABC):
    @abstractmethod
    async def get_schema_names(self) -> List[str]:
        """
        获取数据库管理系统中所有数据库名
        :return:
        """
        ...

    @abstractmethod
    async def get_table_info(self, schema_name: str) -> List[Dict]:
        """
        获取某个数据库中所有表名与表信息
        :param schema_name: 数据库名称
        :return:
        """
        ...

    @abstractmethod
    async def get_columns(self, schema_name: str, table_name: str) -> List[Dict]:
        """
        获取数据库中某个表所有字段信息
        :param schema_name: 数据库名称
        :param table_name: 表名
        :return:
        """
        ...

    @abstractmethod
    async def execute_sql(self, schema_name: str, sql: str) -> List[Dict]:
        """
        在某个数据库执行SQL
        :param schema_name: 数据库名称
        :param sql: 原生SQL语句
        :return:
        """
        ...


class RemoteExecutor(ABC):
    @classmethod
    @abstractmethod
    async def exec_module(cls, **kwargs) -> str:  # type: ignore
        """
        执行远程模块
        :param kwargs:
        :return:
        """
        ...

    @classmethod
    @abstractmethod
    async def exec_task(cls, **kwargs) -> str:  # type: ignore
        """
        执行远程任务
        :param kwargs:
        :return:
        """
        ...


class CICDPlugin(ABC):
    @staticmethod
    async def log(job_id: str, content: str, is_write_log: bool = True, is_write_time: bool = True) -> None:
        """
        记录日志到文件中
        @param job_id: 任务ID
        @param content: 日志内容
        @param is_write_log: 记录日志文件的同时是否通过logger打印日志
        @param is_write_time: 是否在日志每行开头打印时间
        @return:
        """
        time_output = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        base_dir = Path(__file__).resolve().parent.parent
        log_path = f"{base_dir}/logs/job/{job_id}.log"
        if is_write_log:
            Log.info(content)
        async with aiofiles.open(log_path, "a+", encoding="utf-8") as f:
            if is_write_time:
                await f.write(f"{time_output}\t\t{content}\n")
            else:
                await f.write(f"{content}\n")

    @property
    @abstractmethod
    def name(self) -> str:  # type: ignore
        """
        插件名称
        :return:
        """
        ...

    @property
    @abstractmethod
    def remark(self) -> str:  # type: ignore
        """
        插件备注
        :return:
        """
        ...

    @property
    @abstractmethod
    def parameters(self) -> Dict:  # type: ignore
        """
        插件所需参数
        :return:
        """
        ...

    @classmethod
    @abstractmethod
    async def execute(cls, **kwargs) -> None:  # type: ignore
        """
        执行插件功能
        :param kwargs:
        :return:
        """
        ...
