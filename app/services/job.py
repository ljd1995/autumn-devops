import json
from collections import defaultdict
from typing import List, Dict

import aiofiles  # type: ignore
from app.models.cmdb import HostGroup, Host
from app.models.enums import ScriptType
from app.models.job import AdhocHistory, Script, ScriptHistory
from app.schemas.job import ExecModuleReq, ExecTaskReq
from app.schemas.model_creator import ScriptModel
from app.services.children import ChildService
from tortoise.contrib.pydantic import pydantic_model_creator
from utils.crypt import AESCipher, md5_encode_with_salt
from utils.executor import AnsibleExecutor
from aiofiles import os as async_os


class JobService(object):
    @classmethod
    async def _get_inventory(cls, host_group_id: int) -> str:
        host_group_obj = await HostGroup.get(pk=host_group_id)
        host_obj_qs = await host_group_obj.hosts.all()
        if not host_obj_qs:
            children = await host_group_obj.children.all()
            children_ids = [child.id for child in children]
            host_obj_qs = await Host.filter(host_group_id__in=children_ids)
        inventory = {"all": {"hosts": {}}}  # type: ignore
        for host_obj in host_obj_qs:
            inventory["all"]["hosts"][host_obj.intranet_ip] = {
                "ansible_ssh_host": host_obj.intranet_ip,
                "ansible_ssh_user": host_obj.login_user,
                "ansible_ssh_pass": AESCipher.decrypt(host_obj.password),
                "ansible_ssh_port": host_obj.port,
            }
        data = json.dumps(inventory, indent=4)
        filepath = f"/tmp/{md5_encode_with_salt(data)}.json"
        async with aiofiles.open(filepath, "w") as f:
            await f.write(data)
        return filepath

    @classmethod
    async def _remove_file(cls, filepath: str) -> None:
        await async_os.remove(filepath)

    @classmethod
    async def exec_module(cls, param: ExecModuleReq, username: str) -> str:
        body = param.dict(exclude_unset=True)
        host_group_id = body.pop("host_group_id")
        inventory = await cls._get_inventory(host_group_id)
        result = await AnsibleExecutor.exec_module(inventory=inventory, **body)
        # 记录入库
        await AdhocHistory.create(username=username, host_group_id=host_group_id, **body)
        # 删除inventory文件，避免冗余
        await cls._remove_file(inventory)
        return result

    @classmethod
    async def exec_task(cls, param: ExecTaskReq) -> str:
        inventory = await cls._get_inventory(param.host_group_id)
        executable = "bash"
        file_name = ""
        content_md5 = md5_encode_with_salt(param.content)
        match param.exec_command:
            case "ansible":
                executable = "ansible"
                file_name = f"{content_md5}.yml"
            case "py2":
                executable = "python2"
                file_name = f"{content_md5}.py"
            case "py3":
                executable = "python3"
                file_name = f"{content_md5}.py"
            case "shell":
                executable = "bash"
                file_name = f"{content_md5}.sh"
            case "go":
                executable = "go"
                file_name = f"{content_md5}.go"
        # 写入本地文件
        async with aiofiles.open(f"/tmp/{file_name}", "w") as f:
            await f.write(param.content)
        # 远程脚本使用script模块执行，playbook使用ansible执行
        if executable != "ansible":
            result = await AnsibleExecutor.exec_module(
                inventory=inventory,
                host_pattern=param.host_pattern,
                module="script",
                module_args=f"/tmp/{file_name} executable={executable}",
            )
        else:
            result = await AnsibleExecutor.exec_task(
                inventory=inventory,
                playbook=f"/tmp/{file_name}",
            )
        # 删除inventory文件，避免冗余
        await cls._remove_file(inventory)
        # 删除playbook文件，避免冗余
        await cls._remove_file(f"/tmp/{file_name}")
        return result

    @staticmethod
    async def get_children_data() -> List:
        script_obj_qs = await Script.all()
        data = await ChildService.get_children_data(script_obj_qs, ScriptModel)  # type: ignore
        return data

    @staticmethod
    async def get_script_history(item_id: int) -> List:
        script_history_obj_qs = ScriptHistory.filter(script_id=item_id)
        pydantic_model = pydantic_model_creator(ScriptHistory)
        data = await pydantic_model.from_queryset(script_history_obj_qs)
        return data

    @staticmethod
    async def get_all_script_options() -> List:
        script_obj_qs = await Script.filter(node_type=ScriptType.NODE)
        result: Dict[str, list] = defaultdict(list)
        for script_obj in script_obj_qs:
            item = {
                "value": script_obj.id,
                "label": script_obj.name,
            }
            result[script_obj.exec_command].append(item)
        ret = []
        for k, v in result.items():
            tmp_dict = {
                "label": k,
                "options": v,
            }
            ret.append(tmp_dict)
        return ret
