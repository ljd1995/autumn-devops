from typing import Dict, List

import httpx
from common.exceptions import ConfigureException


class NacosConfigure(object):
    def __init__(self, server_addresses: str, namespace: str, username: str, password: str) -> None:
        self._server_addresses = server_addresses
        self._namespace = namespace
        self._username = username
        self._password = password
        self._token = self._generate_token()

    @staticmethod
    async def _http_request(method: str, url: str, params: Dict | None = None, timeout: int = 10) -> httpx.Response:
        if params is None:
            params = {}
        if not url.startswith("http://"):
            url = "http://" + url
        async with httpx.AsyncClient() as client:
            if method == "get":
                r = await client.get(url, params=params, timeout=timeout)
            elif method == "post":
                r = await client.post(url, data=params, timeout=timeout)
            elif method == "put":
                r = await client.put(url, data=params, timeout=timeout)
            elif method == "delete":
                r = await client.delete(url, params=params, timeout=timeout)
            if r.status_code != 200:
                raise ConfigureException("nacos config fail!! status: %d" % r.status_code)
            else:
                return r

    async def _generate_token(self) -> str:
        url = f"{self._server_addresses}/nacos/v1/auth/login"
        params = {
            "username": self._username,
            "password": self._password,
        }
        r = await self._http_request("post", url, params=params)
        return r.json().get("accessToken")

    async def list_all_namespaces(self) -> List:
        url = f"{self._server_addresses}/nacos/v1/console/namespaces?accessToken={self._token}"
        r = await self._http_request("get", url, params=None)
        ns_list = r.json().get("data")
        return [i.get("namespaceShowName") for i in ns_list]

    async def create_namespace(self) -> None:
        url = f"{self._server_addresses}/nacos/v1/console/namespaces?accessToken={self._token}"
        params = {
            "customNamespaceId": self._namespace,
            "namespaceName": self._namespace,
            "namespaceDesc": self._namespace,
        }
        await self._http_request("post", url, params=params)

    async def delete_namespace(self) -> None:
        url = f"{self._server_addresses}/nacos/v1/console/namespaces?accessToken={self._token}"
        params = {
            "namespaceId": self._namespace,
        }
        await self._http_request("delete", url, params=params)

    async def publish_config(self, data_id: str, group: str, content: str, config_type: str = "yaml") -> None:
        # 如果命名空间不存在，则创建命名空间
        ns_list = await self.list_all_namespaces()
        if self._namespace not in ns_list:
            await self.create_namespace()
        url = f"{self._server_addresses}/nacos/v1/cs/configs?accessToken={self._token}"
        params = {"tenant": self._namespace, "dataId": data_id, "group": group, "content": content, "type": config_type}
        await self._http_request("post", url, params=params)

    async def get_config(self, data_id: str, group: str) -> str:
        url = f"{self._server_addresses}/nacos/v1/cs/configs?accessToken={self._token}"
        params = {"tenant": self._namespace, "dataId": data_id, "group": group}
        r = await self._http_request("get", url, params=params)
        return r.text

    def set_key(self, ret: Dict, keys: List, val: str) -> None:
        """
        递归新增或修改key, key类型为a.b.c格式
        @param ret: yaml转换后的字典类型值
        @param keys: a.b.c通过.分割后的数组
        @param val: key值
        @return: 不返回值，会直接对ret做修改
        """
        for i in keys:
            result = ret.get(i)
            # 如果val可以转为int类型，则转为int类型
            try:
                val = int(val)  # type: ignore
            except Exception:
                pass
            if isinstance(result, dict) and len(keys) > 0:
                keys.remove(i)
                self.set_key(result, keys, val)
            elif not isinstance(result, dict):
                keys.remove(i)
                if len(keys) == 0:
                    ret[i] = val
                    break
                else:
                    if not isinstance(result, dict):
                        ret[i] = {}
                    self.set_key(result, keys, val)  # type: ignore
            elif not isinstance(result, dict) and len(keys) == 0:
                ret[i] = val
                break
