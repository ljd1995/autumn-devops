import asyncio

from app.models.cmdb import Host
from app.models.enums import HostType, BelongsTo
from common.log import Log
from config.db import TORTOISE_ORM
from tortoise import Tortoise
from utils.executor import AnsibleExecutor


async def get_data() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    for i in range(2, 25):
        await Host.create(
            intranet_ip=f"192.168.3.{i}",
            external_ip=f"192.168.3.{i}",
            host_type=HostType.LOCAL,
            belongs_to=BelongsTo.IDC,
            login_user="root",
            password="123456",
            port=22,
            remark=f"主机{i}",
            host_group_id=4,
        )


async def get_db_info() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    from sqlalchemy import inspect, MetaData

    # engine = create_async_engine("mysql+asyncmy://root:123456@localhost:3306", echo=True)
    engine = create_async_engine("postgresql+asyncpg://postgres:123456@localhost:5432/demo", echo=False)
    meta = MetaData(bind=engine)
    Log.info(meta)
    async with engine.connect() as conn:
        schemas = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_schema_names())
        Log.info(schemas)
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        Log.info(tables)
        columns = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns("t_user", "public"))
        # Log.info(schemas)

        Log.info(columns)
        for table in tables:
            options = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_comment(table))
            Log.info(options)
    # async_engine = create_async_engine("mysql+asyncmy://root:123456@localhost/autumn", echo=True)
    # async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    # async with async_session() as session:
    #     data = await session.execute("select * from t_host limit 1")


async def ansbile_run() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    a = ["1", "2", "3"]
    x = a.pop(1) if a else None
    print(x)


# host_group = await HostGroup.get(pk=3)
# print(host_group)
# hosts = await host_group.hosts.all()
# for i in hosts:
#     print(i)
# import ansible_runner
#
# out, err = ansible_runner.get_plugin_list()
# print("out: {}".format(out))
# print("err: {}".format(err))

# data_dir = "/tmp"
# # myhosts = "/Users/luojiandong/data/hosts"
# hosts = {
#     "nodes": {
#         "hosts": {
#             "node1": {
#                 "ansible_ssh_host": "192.168.64.6",
#                 "ansible_ssh_user": "root",
#                 "ansible_ssh_pass": "123456",
#                 "ansible_ssh_port": 22,
#             }
#         }
#     }
# }
#
# print("执行module")
# m = ansible_runner.run(
#     private_data_dir=data_dir,
#     inventory=hosts,
#     host_pattern="*",
#     module="setup",
#     quiet=True,
#     json_mode=False,
#     extravars={"ansible_ssh_pass": "123456"},
# )
# data = m.stdout.read()
# data = data.split("=>")[1]
# # print(data)
# ret = json.loads(data)
# result = ret.get("ansible_facts")
#
# distributor = result.get("ansible_lsb").get("id")
# release_version = result.get("ansible_lsb").get("release")
# mem_total = result.get("ansible_memtotal_mb")
# swap_total = result.get("ansible_memory_mb").get("swap").get("total")
# processor_num = result.get("ansible_processor_nproc")
# physical_num = result.get("ansible_processor_count")
# core_num = result.get("ansible_processor_cores")
# kernel_version = result.get("ansible_kernel")
# manufacturer = result.get("ansible_system_vendor")
# product_name = result.get("ansible_product_name")
# sn = result.get("ansible_product_serial")
# uuid = result.get("ansible_product_uuid")
# print(distributor, release_version, kernel_version)
# print(mem_total, swap_total)
# print(processor_num, physical_num, core_num)
# print(manufacturer, product_name, sn, uuid)
# for k, v in result.get("ansible_devices").items():
#     if not k.startswith("loop"):
#         print(k, v)
#         name = k
#         interface_type = "HDD" if v.get("rotational") else "SSD"
#         capacity = v.get("size")
#         print(name, capacity, interface_type)

# print("{}: {}".format(m.status, m.rc))
# # successful: 0
# for each_host_event in m.events:
#     print(each_host_event["event"])
# print("Final status:", m.stats)

# print("执行playbook")
# m = ansible_runner.run(
#     private_data_dir=data_dir,
#     playbook="/Users/luojiandong/data/test.yml",
#     inventory=hosts,
#     extravars={"ansible_test": "test_playbook"},
# )
# print("{}: {}".format(m.status, m.rc))
# # successful: 0
# for each_host_event in m.events:
#     print(each_host_event["event"])
# print("Final status:", m.stats)


async def test_ansible() -> None:
    data_dir = "/tmp"
    hosts = {
        "nodes": {
            "hosts": {
                "node1": {
                    "ansible_ssh_host": "192.168.64.6",
                    "ansible_ssh_user": "root",
                    "ansible_ssh_pass": "123456",
                    "ansible_ssh_port": 22,
                }
            }
        }
    }

    result = await AnsibleExecutor.exec_task(
        data_dir=data_dir,
        inventory=hosts,
        playbook="/Users/luojiandong/data/test.yml",
    )
    print(result)


# async def get_children_data() -> list:
#     await Tortoise.init(config=TORTOISE_ORM)
#
#     async def _get_children_data(obj: Model, model_pydantic: Type[PydanticModel]) -> dict:
#         childrens = await obj.children.all()  # type: ignore
#         ret = await model_pydantic.from_tortoise_orm(obj)
#         result = ret.dict()
#         children_list = []
#         for children in childrens:
#             ret = await _get_children_data(children, model_pydantic)
#             children_list.append(ret)
#         hosts = obj.hosts.all()  # type: ignore
#         hosts_data = await HostModel.from_queryset(hosts)
#         if hosts_data and children_list == []:
#             children_list = hosts_data
#         result["children"] = children_list
#         return result
#
#     queryset = await HostGroup.all()
#     data = []
#     for obj in queryset:
#         if not obj.parent:  # type: ignore
#             item = await _get_children_data(obj, HostGroupModel)
#             data.append(item)
#     print(jsonable_encoder(data))
#     return data


if __name__ == "__main__":
    asyncio.run(ansbile_run())
