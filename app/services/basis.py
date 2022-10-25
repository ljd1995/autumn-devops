from typing import List, Dict, Type

from app.models.basis import HostGroup, Host
from app.schemas.basis import AssociateHostGroupReq, GetDbSchemaReq, DbExecuteSqlReq, GetDbColumnReq, GetDbTableReq
from app.schemas.model_creator import HostGroupModel
from app.services.children import ChildService
from tortoise.contrib.pydantic import PydanticModel
from tortoise.models import MODEL, Model
from tortoise.queryset import QuerySet
from utils.abstract import DbOperator
from utils.operator import MysqlOperator, PostgresqlOperator


class HostService(object):
    @staticmethod
    async def get_page_queryset(queryset: QuerySet[MODEL], item: Dict) -> QuerySet[MODEL]:
        if "host_group_id" in item:
            hosts = await queryset.filter(host_group_id=item["host_group_id"])
            if not hosts:
                host_group_id = item.pop("host_group_id")
                host_group_obj = await HostGroup.get(pk=host_group_id)
                children = await host_group_obj.children.all()
                children_ids = [child.id for child in children]
                queryset = queryset.filter(host_group_id__in=children_ids).filter(**item)
                return queryset
            else:
                return queryset.filter(**item)
        else:
            return queryset.filter(**item)

    @staticmethod
    async def associate_host_group(param: AssociateHostGroupReq) -> None:
        await Host.filter(pk__in=param.host_ids).update(host_group_id=param.host_group_id)


class HostGroupService(object):
    @staticmethod
    async def get_children_data() -> List:
        host_group_obj_qs = await HostGroup.all()
        data = await ChildService.get_children_data(host_group_obj_qs, HostGroupModel)  # type: ignore
        return data

    @staticmethod
    async def get_children_data_with_host() -> List:
        async def _get_children_data(obj: Model, model_pydantic: Type[PydanticModel]) -> dict:
            childrens = await obj.children.all()  # type: ignore
            ret = await model_pydantic.from_tortoise_orm(obj)
            result = ret.dict()
            children_list = []
            for children in childrens:
                ret = await _get_children_data(children, model_pydantic)  # type: ignore
                children_list.append(ret)
            host_obj_qs = await obj.hosts.all()  # type: ignore
            hosts_data = []
            for host_obj in host_obj_qs:
                item = {
                    "key": f"host-{host_obj.external_ip}-{host_obj.id}",
                    # Ant-Design-Vue3 Tree组件会校验KEY，KEY如果重复会导致展示异常，故key加前缀来避免
                    "title": f"{host_obj.external_ip}({host_obj.remark})",
                }
                hosts_data.append(item)
            if hosts_data and children_list == []:
                children_list = hosts_data  # type: ignore
            result["children"] = children_list
            return result

        host_group_obj_qs = await HostGroup.all()
        data = await ChildService.get_children_data(
            host_group_obj_qs, HostGroupModel, children_handler=_get_children_data  # type: ignore
        )
        return data


class DbService(object):
    @classmethod
    def _get_db_operator(cls, param: GetDbSchemaReq) -> DbOperator:
        db_url = f"{param.username}:{param.password}@{param.host}:{param.port}"
        op: DbOperator = None  # type: ignore
        if param.db_type in ("mysql", "maria"):
            op = MysqlOperator(db_url)
        elif param.db_type == "pg":
            op = PostgresqlOperator(db_url)
        return op

    @classmethod
    async def get_schema_names(cls, param: GetDbSchemaReq) -> List:
        data = await cls._get_db_operator(param).get_schema_names()
        return data

    @classmethod
    async def get_table_info(cls, param: GetDbTableReq) -> List:
        data = await cls._get_db_operator(param).get_table_info(param.schema_name)
        return data

    @classmethod
    async def get_columns(cls, param: GetDbColumnReq) -> List:
        data = await cls._get_db_operator(param).get_columns(param.schema_name, param.table_name)
        return data

    @classmethod
    async def execute_sql(cls, param: DbExecuteSqlReq) -> List:
        data = await cls._get_db_operator(param).execute_sql(param.schema_name, param.sql)
        return data
