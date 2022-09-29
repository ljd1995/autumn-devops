from typing import List, Dict

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.abstract import DbOperator


class MysqlOperator(DbOperator):
    _instance = None

    def __new__(cls, *args, **kwargs):  # type: ignore
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, db_url: str, pool_size: int = 100, pool_recycle: int = 30):
        _db_url = f"mysql+aiomysql://{db_url}"
        self._pool_size = pool_size
        self._pool_recycle = pool_recycle
        self._engine = create_async_engine(_db_url, echo=False, pool_size=pool_size, pool_recycle=pool_recycle)
        self._db_url = _db_url

    async def get_schema_names(self) -> List[str]:
        async with self._engine.connect() as conn:
            schemas = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_schema_names())
            return schemas

    async def get_table_info(self, schema_name: str) -> List[Dict]:
        async with self._engine.connect() as conn:
            tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names(schema_name))
            result = []
            for table in tables:
                options = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn).get_table_options(table, schema_name)
                )
                item = {
                    "table_name": table,
                    "table_comment": options.get("mysql_comment", ""),
                    "table_engine": options.get("mysql_engine", ""),
                    "table_default_charset": options.get("mysql_default charset", ""),
                }
                result.append(item)
            return result

    async def get_columns(self, schema_name: str, table_name: str) -> List[Dict]:
        async with self._engine.connect() as conn:
            columns = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns(table_name, schema_name))
            result: List[Dict] = []
            for column in columns:
                column["type"] = str(column["type"])
                try:
                    column["default"] = eval(column["default"])
                except Exception:
                    pass
                result.append(column)
            return result

    async def execute_sql(self, schema_name: str, sql: str) -> List[Dict]:
        engine = create_async_engine(
            f"{self._db_url}/{schema_name}", echo=False, pool_size=self._pool_size, pool_recycle=self._pool_recycle
        )
        async_session = sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            data = await session.execute(sql)
            return list(data)


class PostgresqlOperator(DbOperator):
    _instance = None

    def __new__(cls, *args, **kwargs):  # type: ignore
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, db_url: str, pool_size: int = 100, pool_recycle: int = 30):
        _db_url = f"postgresql+asyncpg://{db_url}"
        self._pool_size = pool_size
        self._pool_recycle = pool_recycle
        self._engine = create_async_engine(_db_url, echo=False, pool_size=pool_size, pool_recycle=pool_recycle)
        self._db_url = _db_url

    async def get_schema_names(self) -> List[str]:
        async_session = sessionmaker(self._engine, class_=AsyncSession)
        async with async_session() as session:
            sql = "SELECT datname FROM pg_database ORDER BY datname;"
            data = await session.execute(sql)
            return [i[0] for i in data]

    async def get_table_info(self, schema_name: str) -> List[Dict]:
        engine = create_async_engine(
            f"{self._db_url}/{schema_name}", echo=False, pool_size=self._pool_size, pool_recycle=self._pool_recycle
        )
        async with engine.connect() as conn:
            tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            result = []
            for table in tables:
                options = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_comment(table))
                item = {
                    "table_name": table,
                    "table_comment": options.get("text", ""),
                }
                result.append(item)
            return result

    async def get_columns(self, schema_name: str, table_name: str) -> List[Dict]:
        engine = create_async_engine(
            f"{self._db_url}/{schema_name}", echo=False, pool_size=self._pool_size, pool_recycle=self._pool_recycle
        )
        async with engine.connect() as conn:
            columns = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns(table_name, "public"))
            result: List[Dict] = []
            for column in columns:
                column["type"] = str(column["type"])
                try:
                    column["default"] = eval(column["default"])
                except Exception:
                    pass
                result.append(column)
            return result

    async def execute_sql(self, schema_name: str, sql: str) -> List[Dict]:
        engine = create_async_engine(
            f"{self._db_url}/{schema_name}", echo=False, pool_size=self._pool_size, pool_recycle=self._pool_recycle
        )
        async_session = sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            data = await session.execute(sql)
            return list(data)
