from abc import ABC, abstractmethod
from typing import List, Dict


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
