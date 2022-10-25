import asyncio
import datetime
import re
from pathlib import Path
from typing import Dict

import aiofiles
import aiomysql
import asyncpg
import httpx
import yaml
from aiopath import AsyncPath
from app.models.basis import Db, ConfigCenter, DeployConfig
from common.exceptions import (
    CmdExecuteException,
    GitOperateException,
    BuildOperateException,
    DockerOperateException,
    HelmOperateException,
    SqlExecuteException,
    ConfigureException,
    WebhookException,
)
from common.log import Log
from config.setting import settings
from utils.abstract import CICDPlugin
from utils.configure import NacosConfigure
from utils.crypt import AESCipher, md5_encode


class CmdPlugin(CICDPlugin):
    """
    shell命令行执行插件
    """

    @property
    def name(self) -> str:
        return "shell命令行执行"

    @property
    def remark(self) -> str:
        return "主要用于执行shell命令"

    @property
    def parameters(self) -> Dict:
        return {"cmd": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "job_id": "",
            "cmd": "",
        }
        :return:
        """
        try:
            job_id = kwargs.get("job_id")
            cmd = kwargs.get("cmd", "")

            if job_id:
                base_dir = Path(__file__).resolve().parent.parent
                log_path = f"{base_dir}/logs/job/{job_id}.log"
                async with aiofiles.open(log_path, "a+", encoding="utf-8") as f:
                    proc = await asyncio.create_subprocess_shell(cmd, stdout=f, stderr=f, shell=True)  # type: ignore
            else:
                proc = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True  # type: ignore
                )
            stdout, stderr = await proc.communicate()

            # 将git token 修改为******格式，避免日志泄露token
            if "outh2:" in cmd:
                result = re.match(".*outh2:(.*)@.*", cmd)
                assert result is not None
                cmd = cmd.replace(result.group(1), "************")

            if job_id:
                await cls.log(job_id=job_id, content=f"[{cmd!r} exited with {proc.returncode}]")
            else:
                if stdout:
                    Log.info(f"[stdout]\n{stdout.decode()}")
                if stderr:
                    Log.error(f"[stderr]\n{stderr.decode()}")

            if proc.returncode != 0:
                raise CmdExecuteException(f"[{cmd!r} exited with {proc.returncode}]")
        except Exception as e:
            Log.exception(e)
            raise CmdExecuteException(str(e))


class GitPlugin(CICDPlugin):
    """
    Git操作插件
    """

    @property
    def name(self) -> str:
        return "Git操作"

    @property
    def remark(self) -> str:
        return "主要用于git clone代码"

    @property
    def parameters(self) -> Dict:
        return {"git_url": "", "config_id": "", "branch_name": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "git_url": "",
            "branch_name": "",
            "config_id": "",
            "job_id": "",
        }
        :return:
        """
        try:
            git_url = kwargs.get("git_url", "")
            job_id = kwargs.get("job_id", "")
            branch_name = kwargs.get("branch_name")
            config_id = kwargs.get("config_id")

            config_obj = await DeployConfig.filter(pk=config_id).first()
            token = AESCipher.decrypt(config_obj.parameters.token)  # type: ignore

            git_url = git_url.replace("//", f"//outh2:{token}@")
            dir_name = git_url.split("/")[-1].split(".")[0]

            # 使用浅克隆，--depth 1可以在克隆的时候只克隆最新的记录而不克隆git仓库中的历史记录，从而减少克隆大小，大大提高克隆速度
            cmd = (
                f"mkdir -p {settings.GIT_DEST_DIR}/{job_id} && cd {settings.GIT_DEST_DIR}/{job_id} && rm -rf {dir_name}"
                f"&& git clone --depth=1 -b {branch_name} {git_url} && cd {dir_name} && git log {branch_name} -1"
            )

            await CmdPlugin.execute(cmd=cmd, job_id=job_id)
        except Exception as e:
            raise GitOperateException(str(e))


class BuildPlugin(CICDPlugin):
    """
    代码编译插件
    """

    @property
    def name(self) -> str:
        return "代码编译"

    @property
    def remark(self) -> str:
        return "主要用于代码编译，支持多种编译方式"

    @property
    def parameters(self) -> Dict:
        return {"cmd": "", "docker_image_name": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "cmd": "",
            "docker_image_name": "",
            "job_id": "",
        }
        :return:
        """
        try:
            docker_image_name = kwargs.get("docker_image_name")
            job_id = kwargs.get("job_id", "")
            cmd = kwargs.get("cmd")
            run_cmd = f"docker run --rm -v {settings.GIT_DEST_DIR}:/opt {docker_image_name} /bin/bash -c '{cmd}'"
            await CmdPlugin.execute(cmd=run_cmd, job_id=job_id)
        except Exception as e:
            raise BuildOperateException(str(e))


class DockerPlugin(CICDPlugin):
    """
    docker插件
    """

    @property
    def name(self) -> str:
        return "docker操作"

    @property
    def remark(self) -> str:
        return "主要用于构建docker镜像"

    @property
    def parameters(self) -> Dict:
        return {"config_id": "", "image_tag": "", "image_name": "", "module_name": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "config_id": "",
            "module_name": "",
            "image_name": "",
            "image_tag": "",
            "job_id": "",
        }
        :return:
        """
        try:
            config_id = kwargs.get("config_id")
            module_name = kwargs.get("module_name")
            image_name = kwargs.get("image_name")
            job_id = kwargs.get("job_id", "")
            if not (image_tag := kwargs.get("image_tag")):
                image_tag = datetime.datetime.now().strftime("%Y%m%d%H%M")

            config_obj = await DeployConfig.filter(pk=config_id).first()
            registry = config_obj.parameters.registry  # type: ignore

            registry_password_path = AsyncPath(f"/etc/docker_passwd{config_id}")
            if not await registry_password_path.exists():
                async with aiofiles.open(registry_password_path, "w") as f:
                    password = AESCipher.decrypt(config_obj.parameters.password)  # type: ignore
                    await f.write(password)

            docker_image_url = f"{registry}/{module_name}/{image_name}:{image_tag}"  # type: ignore
            docker_login_cmd = (
                f"cd {settings.GIT_DEST_DIR}/{job_id}/{image_name} && cat /etc/docker_passwd{config_id} | "
                f"docker login -u {config_obj.parameters.username} --password-stdin {registry}"  # type: ignore
            )
            docker_build_cmd = f"docker build  -t  {docker_image_url} . "
            docker_push_cmd = f"docker push  {docker_image_url}"
            build_cmd = f"{docker_login_cmd} && {docker_build_cmd} && {docker_push_cmd}"

            await CmdPlugin.execute(cmd=build_cmd, job_id=job_id)
        except Exception as e:
            raise DockerOperateException(str(e))


class HelmPlugin(CICDPlugin):
    """
    helm安装插件
    """

    @property
    def name(self) -> str:
        return "helm安装"

    @property
    def remark(self) -> str:
        return "主要用于执行helm操作，发布到k8s"

    @property
    def parameters(self) -> Dict:
        return {"k8s_config_id": "", "namespace": "", "module_name": "", "service_name": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "config_id": "",
            "namespace": "",
            "service_name": "",
            "module_name": "",
            "job_id": "",
        }
        :return:
        """
        try:
            config_id = kwargs.get("config_id")
            job_id = kwargs.get("job_id", "")
            namespace = kwargs.get("namespace")
            service_name = kwargs.get("service_name")
            module_name = kwargs.get("module_name")
            chart_dir = f"/opt/chart/{job_id}/{module_name}"

            config_obj = await DeployConfig.filter(pk=config_id).first()

            kube_name = f"/etc/{md5_encode(config_obj.parameters.address)}.yml"  # type: ignore
            kube_path = AsyncPath(kube_name)
            if not await kube_path.exists():
                async with aiofiles.open(kube_name, "w") as f:
                    config_yaml = AESCipher.decrypt(config_obj.parameters.config_yaml)  # type: ignore
                    await f.write(config_yaml)
                # 将kubeconfig文件设置权限，避免warning输出
                await CmdPlugin.execute(cmd=f"chmod g-rw {kube_name} && chmod o-r {kube_name}", job_id=job_id)

            cmd = f"cd {chart_dir} && helm -n {namespace} upgrade {service_name} . --install --kubeconfig={kube_path}"

            await CmdPlugin.execute(cmd=cmd, job_id=job_id)
        except Exception as e:
            raise HelmOperateException(str(e))


class SqlPlugin(CICDPlugin):
    """
    sql执行插件
    """

    @property
    def name(self) -> str:
        return "sql执行"

    @property
    def remark(self) -> str:
        return "主要用于执行SQL（不能用于创库）"

    @property
    def parameters(self) -> Dict:
        return {"sql": "", "db_id": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "db_id": "",
            "sql": "",
            "job_id": "",
        }
        :return:
        """
        try:
            db_id = kwargs.get("db_id")
            sql = kwargs.get("sql")
            # job_id = kwargs.get("job_id")

            db_cbj = await Db.filter(pk=db_id).first()
            assert db_cbj is not None
            db_type = db_cbj.db_type
            password = AESCipher.decrypt(db_cbj.admin_password)

            if db_type == "mysql":
                conn = await aiomysql.connect(
                    host=db_cbj.address,
                    port=int(db_cbj.port),
                    user=db_cbj.admin_user,
                    password=password,
                    db=db_cbj.db_name,
                )
                async with conn.cursor() as cur:
                    try:
                        await cur.execute(sql)
                        await conn.commit()
                    except Exception as e:
                        await conn.rollback()
                        raise SqlExecuteException(str(e))
                conn.close()
            elif db_type == "pg":
                conn = await asyncpg.connect(
                    host=db_cbj.address,
                    port=int(db_cbj.port),
                    user=db_cbj.admin_user,
                    password=password,
                    database=db_cbj.db_name,
                )
                async with conn.transaction():
                    await conn.execute(sql)
        except Exception as e:
            raise SqlExecuteException(str(e))


class ConfigurePlugin(CICDPlugin):
    """
    配置中心修改配置插件
    """

    @property
    def name(self) -> str:
        return "配置修改"

    @property
    def remark(self) -> str:
        return "主要用于在配置中心中修改配置（遵循x.x.x语法，只支持yaml格式配置文件）"

    @property
    def parameters(self) -> Dict:
        return {
            "key": "",
            "group": "",
            "content": "",
            "data_id": "",
            "namespace": "",
            "config_center_id": "",
        }

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "config_center_id": "",
            "namespace": "",
            "data_id": "",
            "group": "",
            "key": "",
            "content": "",
            "job_id": "",
        }
        :return:
        """
        try:
            config_center_id = kwargs.get("config_center_id")
            namespace = kwargs.get("namespace", "")
            data_id = kwargs.get("data_id", "")
            group = kwargs.get("group", "")
            key = kwargs.get("key", "")
            content = kwargs.get("content", "")

            config_center_obj = await ConfigCenter.filter(pk=config_center_id).first()
            assert config_center_obj is not None
            config_type = config_center_obj.type

            if config_type == "nacos":
                na = NacosConfigure(
                    server_addresses=config_center_obj.address,
                    namespace=namespace,
                    username=config_center_obj.username,
                    password=config_center_obj.password,
                )
                result = await na.get_config(data_id, group)
                ret = yaml.load(result, Loader=yaml.FullLoader)
                na.set_key(ret, key.split("."), content)
                await na.publish_config(data_id=data_id, group=group, content=yaml.dump(ret))
        except Exception as e:
            raise ConfigureException(str(e))


class WebhookPlugin(CICDPlugin):
    """
    Webhook推送插件
    """

    @property
    def name(self) -> str:
        return "Webhook推送"

    @property
    def remark(self) -> str:
        return "主要用于执行Webhook推送"

    @property
    def parameters(self) -> Dict:
        return {"url": ""}

    @classmethod
    async def execute(cls, **kwargs: str) -> None:
        """
        :param kwargs: 参数例子
        {
            "url": "",
            "job_id": "",
        }
        :return:
        """
        try:
            url = kwargs.get("url", "")
            async with httpx.AsyncClient() as client:
                r = await client.post(url, timeout=20)
                if r.status_code != 200:
                    raise WebhookException("webhook fail!! status: %d" % r.status_code)
        except Exception as e:
            raise WebhookException(str(e))
