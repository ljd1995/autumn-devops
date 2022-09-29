import asyncio
import re
import threading
from typing import List

import aiofiles  # type: ignore
import orjson
import paramiko  # type: ignore
from aiofiles import os as async_os
from app.models.audit import SSHAuditRecord
from app.models.cmdb import Host
from app.models.enums import SSHStatus
from common.exceptions import SSHOperatorException
from common.log import Log
from common.make import run_async
from config.setting import settings
from fastapi import WebSocket
from orjson import JSONDecodeError
from paramiko import SSHClient, Channel, SSHException, SFTPClient
from starlette.websockets import WebSocketState
from utils.crypt import AESCipher, md5_encode_with_salt


class TerminalService(object):
    def __init__(self, websocket: WebSocket, username: str) -> None:
        self.websocket: WebSocket = websocket
        self.username: str = username
        self.ssh_client: SSHClient | None = None
        self.channel: Channel | None = None
        self.sftp_client: SFTPClient | None = None
        self.ssh_audit_record_obj: SSHAuditRecord | None = None
        self.upload_file_name: str = "tmp_name"
        self.cmd: List[str] = []  # 所有命令
        self.cmd_tmp: str = ""  # 一行命令
        self.tab_mode: bool = False  # 使用tab命令补全时需要读取返回数据然后添加到当前输入命令后
        self.history_mode: bool = False
        self.index: int = 0

    async def _send_message(self, message: str, *, message_type: str = "content") -> None:
        if self.websocket and self.websocket.client_state == WebSocketState.CONNECTED:
            msg = {"type": message_type, "data": message}
            await self.websocket.send_json(msg)

    def _get_ssh_client(self, host_obj: Host, proxy_host_obj: Host) -> str | None:
        try:
            # 初始化ssh_client
            self.ssh_client = paramiko.SSHClient()
            # 当远程服务器没有本地主机的密钥时自动添加到本地，这样不用在建立连接的时候输入yes或no进行确认
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if proxy_host_obj:
                # 通过代理主机连接远程主机，一般该代理主机为运维过程中的跳板机
                proxy = paramiko.SSHClient()
                proxy.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                proxy.connect(
                    hostname=proxy_host_obj.external_ip,
                    username=proxy_host_obj.login_user,
                    port=proxy_host_obj.port,
                    password=AESCipher.decrypt(proxy_host_obj.password),
                    timeout=settings.SSH_CONNECT_TIMEOUT,
                )
                sock = proxy.get_transport().open_channel(
                    "direct-tcpip",
                    (host_obj.external_ip, host_obj.port),
                    (proxy_host_obj.external_ip, proxy_host_obj.port),
                )
                # 代理连接SSH服务器
                self.ssh_client.connect(
                    hostname=host_obj.external_ip,
                    username=host_obj.login_user,
                    port=host_obj.port,
                    password=AESCipher.decrypt(host_obj.password),
                    timeout=settings.SSH_CONNECT_TIMEOUT,
                    sock=sock,
                )
            else:
                # 直连SSH服务器
                self.ssh_client.connect(
                    hostname=host_obj.external_ip,
                    username=host_obj.login_user,
                    port=host_obj.port,
                    password=AESCipher.decrypt(host_obj.password),
                    timeout=settings.SSH_CONNECT_TIMEOUT,
                )
            # 打开ssh通道，建立长连接
            transport = self.ssh_client.get_transport()
            # 至关重要的代码，保持ssh连接不会主动断开（即websocket未断开时，ssh应该保持连接）
            transport.set_keepalive(30)
            # 打开sftp
            self.sftp_client = transport.open_sftp_client()
            # 获取ssh通道
            self.channel = transport.open_session()
            # 获取伪pty，并设置term和终端大小,width,height不能设置太小，否则前端显示时，横向输入和纵向输入会变化
            self.channel.get_pty(term="xterm-256color", width=188, height=49)
            # 激活终端
            self.channel.invoke_shell()
            # 获取首次连接返回数据
            recv = self.channel.recv(1024 * 10).decode("utf-8", "ignore")
            return recv
        except Exception as e:
            Log.exception(e)
            return None

    async def _channel_to_socket(self) -> None:
        # 获取伪tty发送回的数据并发送到前端
        while not self.channel.exit_status_ready():  # type: ignore
            try:
                data = self.channel.recv(2048).decode("utf-8", "ignore")  # type: ignore
                await self._send_message(data)
                if self.tab_mode:
                    tmp = data.split(" ")
                    if len(tmp) == 2 and tmp[1] == "" and tmp[0] != "":
                        self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b"\x07", b"").decode()
                    elif len(tmp) == 1 and tmp[0].encode() != b"\x07":  # \x07 蜂鸣声
                        self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b"\x07", b"").decode()
                    self.tab_mode = False
                if self.history_mode:
                    self.index = 0
                    if data.strip() != "":
                        self.cmd_tmp = re.sub(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]|\x08", "", data)
                    self.history_mode = False
            except Exception as e:
                Log.exception(e)
                if self.ssh_client:
                    self.ssh_client.close()
                if self.sftp_client:
                    self.sftp_client.close()
                if self.websocket:
                    await self.websocket.close()
                break

    def _get_file(self, remote_path: str, local_path: str) -> None:
        if self.sftp_client:
            self.sftp_client.get(remote_path, local_path)

    def _put_file(self, local_path: str, remote_path: str) -> None:
        if self.sftp_client:
            self.sftp_client.put(local_path, remote_path)

    async def _delete_file(self, local_path: str) -> None:
        # 删除上传下载时临时生成在本地的文件
        await async_os.remove(local_path)

    async def _upload_file(self, remote_path: str, file_bytes: bytes) -> None:
        try:
            file_name_md5 = md5_encode_with_salt(remote_path)
            local_path = f"/tmp/{file_name_md5}"
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(file_bytes)
            await run_async(self._put_file, local_path, remote_path)
            await self._send_message(f"上传文件成功，文件保存在：{remote_path}", message_type="success")
            # 删除上传时临时生成在本地的文件
            await self._delete_file(local_path)
        except Exception as e:
            await self._send_message(f"上传文件失败，{str(e)}", message_type="error")

    async def _download_file(self, remote_path: str) -> None:
        try:
            file_name = remote_path.split("/")[-1]
            file_suffix = file_name.split(".")[-1]
            file_name_md5 = md5_encode_with_salt(remote_path)
            file_path = f"{file_name_md5}.{file_suffix}" if file_suffix else file_name_md5
            local_path = f"/tmp/{file_path}"
            await run_async(self._get_file, remote_path, local_path)
            await self._send_message(file_name, message_type="file")
            async with aiofiles.open(local_path, "rb") as f:
                data = await f.read()
                await self.websocket.send_bytes(data)
            # 删除下载时临时生成在本地的文件
            await self._delete_file(local_path)
        except Exception as e:
            await self._send_message(f"下载文件失败，{str(e)}", message_type="error")

    async def connect(self, host_id: int) -> None:
        # 根据前端传入的host_id，获取服务器用户名密码
        host_obj = await Host.get(pk=host_id)
        # 获取代理主机信息
        proxy_ips = host_obj.proxy_ips
        proxy_host_obj = None
        # 主机有配置代理时，走配置的代理，如果配置有多个代理，则走最后一次配置的代理，如果没有配置，则判断系统是否配置主机统一走默认代理，有则走默认代理
        if proxy_ips:
            proxy_ip = proxy_ips.split(",")[-1]
            proxy_host_obj = await Host.filter(external_ip=proxy_ip).first()
        elif settings.SSH_UNIT_PROXY and settings.SSH_UNIT_PROXY_IP:
            proxy_host_obj = await Host.filter(external_ip=settings.SSH_UNIT_PROXY_IP).first()
        recv = await run_async(self._get_ssh_client, host_obj, proxy_host_obj)
        if recv:
            await self.websocket.accept()
            await self._send_message(recv)
            self.ssh_audit_record_obj = await SSHAuditRecord.create(
                username=self.username,
                ssh_host=host_obj.external_ip,
                ssh_user=host_obj.login_user,
                proxy_host=proxy_host_obj.external_ip if proxy_host_obj else "",
                status=SSHStatus.ONLINE,
                ssh_command="",
            )
            # 新起一个线程，避免堵塞
            _thread = threading.Thread(target=asyncio.run, args=(self._channel_to_socket(),), daemon=True)
            _thread.start()
        else:
            raise SSHOperatorException("SSH连接发生异常，websocket不接受连接")

    async def disconnect(self) -> None:
        self.handle_cmd()
        if self.ssh_audit_record_obj:
            self.ssh_audit_record_obj.ssh_command = ",".join(self.cmd)
            self.ssh_audit_record_obj.status = SSHStatus.OFFLINE
            await self.ssh_audit_record_obj.save()
        self.ssh_client.close()  # type: ignore

    async def receive(self, text_data: str, bytes_data: bytes) -> None:
        try:
            if text_data:
                if "data" in text_data and "type" in text_data:
                    result = orjson.loads(text_data)
                    content_type = result.get("type")
                    data = result.get("data")
                    if content_type == "resize":
                        if self.channel:
                            self.channel.resize_pty(width=data.get("cols"), height=data.get("rows"))  # type: ignore
                    elif content_type == "content":
                        self.gen_cmd(data)
                        self.channel.send(data)  # type: ignore
                    elif content_type == "heartbeat":
                        await self._send_message("pong", message_type="heartbeat")
                    elif content_type == "download":
                        await self._download_file(data)
                    elif content_type == "upload":
                        self.upload_file_name = data
                else:
                    self.channel.send(text_data)  # type: ignore
            if bytes_data:
                remote_path = f"{settings.SFTP_UPLOAD_DIR}/{self.upload_file_name}"
                await self._upload_file(remote_path, bytes_data)
        except SSHException as e:
            Log.exception(e)
        except JSONDecodeError:
            self.channel.send(text_data)  # type: ignore
        except Exception as e:
            Log.exception(e)

    def gen_cmd(self, text_data: str) -> None:
        """
        获取命令脚本源自：https://github.com/pythonzm/Ops
        :param text_data:
        :return:
        """
        if text_data == "\r":
            self.index = 0
            if self.cmd_tmp.strip() != "":
                self.cmd.append(self.cmd_tmp)
                self.cmd_tmp = ""
        elif text_data.encode() == b"\x07":
            pass
        elif text_data.encode() in (b"\x03", b"\x01"):  # ctrl+c 和 ctrl+a
            self.index = 0
        elif text_data.encode() == b"\x05":  # ctrl+e
            self.index = len(self.cmd_tmp) - 2
        elif text_data.encode() == b"\x1b[D":  # ← 键
            if self.index == 0:
                self.index = len(self.cmd_tmp) - 2
            else:
                self.index -= 1
        elif text_data.encode() == b"\x1b[C":  # → 键
            self.index += 1
        elif text_data.encode() == b"\x7f":  # Backspace键
            if self.index == 0:
                self.cmd_tmp = self.cmd_tmp[:-1]
            else:
                self.cmd_tmp = self.cmd_tmp[: self.index] + self.cmd_tmp[self.index + 1 :]
        else:
            if text_data == "\t" or text_data.encode() == b"\x1b":  # \x1b 点击2下esc键也可以补全
                self.tab_mode = True
            elif text_data.encode() == b"\x1b[A" or text_data.encode() == b"\x1b[B":
                self.history_mode = True
            else:
                if self.index == 0:
                    self.cmd_tmp += text_data
                else:
                    self.cmd_tmp = self.cmd_tmp[: self.index] + text_data + self.cmd_tmp[self.index :]

    def handle_cmd(self) -> None:  # 将vim或vi编辑文档时的操作去掉
        vi_index = None
        fg_index = None  # 捕捉使用ctrl+z将vim放到后台的操作
        q_index = None
        q_keys = (":wq", ":q", ":q!")
        for index, value in enumerate(self.cmd):
            if "vi" in value:
                vi_index = index
            if any([key in value for key in q_keys]):
                q_index = index
            if "\x1a" in value:  # \x1a代表ctrl+z
                self.cmd[index] = value.split("\x1a")[1]
            if "fg" in value:
                fg_index = index

        first_index = fg_index if fg_index else vi_index
        if vi_index:
            self.cmd = self.cmd[: first_index + 1] + self.cmd[q_index + 1 :]  # type: ignore
