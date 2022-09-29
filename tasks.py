from common.log import Log
from config.setting import settings
from rearq import ReArq

rearq_obj = ReArq(
    db_url=settings.DB_ADDRESS,
    redis_url=settings.REDIS_ADDRESS,
    delay_queue_num=5,
    keep_job_days=7,
    expire=60,
    job_retry=0,
    trace_exception=True,
)


@rearq_obj.on_shutdown
async def on_shutdown() -> None:
    Log.debug("rearq is shutdown")


@rearq_obj.on_startup
async def on_startup() -> None:
    Log.debug("rearq is startup")


# @rearq_obj.task(cron="*/1 * * * * ")
# async def get_host_info() -> None:
#     data_dir = "/tmp"
#     hosts = {"all": {"hosts": {}}}  # type: ignore
#     host_obj_qs = await Host.all()
#     for host_obj in host_obj_qs:
#         hosts["all"]["hosts"][host_obj.intranet_ip] = {
#             "ansible_ssh_host": host_obj.intranet_ip,
#             "ansible_ssh_user": host_obj.login_user,
#             "ansible_ssh_pass": AESCipher.decrypt(host_obj.password),
#             "ansible_ssh_port": host_obj.port,
#         }
#     data = await AnsibleExecutor.exec_task(data_dir=data_dir, inventory=hosts, module="setup")
#
#     ret = json.loads(data.split("=>")[1])
#     result = ret.get("ansible_facts")
#
#     distributor = result.get("ansible_lsb").get("id")
#     release_version = result.get("ansible_lsb").get("release")
#     mem_total = result.get("ansible_memtotal_mb")
#     swap_total = result.get("ansible_memory_mb").get("swap").get("total")
#     processor_num = result.get("ansible_processor_nproc")
#     physical_num = result.get("ansible_processor_count")
#     core_num = result.get("ansible_processor_cores")
#     kernel_version = result.get("ansible_kernel")
#     manufacturer = result.get("ansible_system_vendor")
#     product_name = result.get("ansible_product_name")
#     sn = result.get("ansible_product_serial")
#     uuid = result.get("ansible_product_uuid")
#     for k, v in result.get("ansible_devices").items():
#         if not k.startswith("loop"):
#             name = k
#             interface_type = "HDD" if v.get("rotational") else "SSD"
#             capacity = v.get("size")
