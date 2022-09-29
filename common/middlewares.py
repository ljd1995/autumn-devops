import json
import time

from app.models.audit import OperatorAuditRecord
from app.models.rbac import User
from core.security import get_current_username
from fastapi import Request, FastAPI, Response
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import Message


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def set_body(self, request: Request) -> None:
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # GET请求直接放行，不记录GET请求日志
        # 如果是文件上传请求，则直接放行
        if request.method.upper() == "GET" or request.url.path.startswith(("/api/v1/wiki/page/file", "/rearq")):
            response = await call_next(request)
            return response

        # 获取响应前自定义操作
        start_time = time.perf_counter()
        await self.set_body(request)
        body = await request.body()
        request_method = request.method

        try:
            request_body = await request.json() if body else ""
        except Exception:
            request_body = ""

        if request.url.path == "/api/v1/token" and request_method.upper() == "POST":
            # 登录接口时，将请求报文中的密码加密，避免暴露
            request_body["password"] = User.generate_hash(request_body.get("password"))
            username = request_body.get("username")
        else:
            username = await get_current_username(request)

        # 获取响应
        response = await call_next(request)

        # 获取到响应后自定义操作
        response_body = [chunk async for chunk in response.body_iterator]  # type: ignore
        response.body_iterator = iterate_in_threadpool(iter(response_body))  # type: ignore
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(round(process_time, 5))

        # 操作日志接口不记录日志
        if not request.url.path.startswith(("/api/v1/audit/operator-history", "/api/v1/audit/ssh-history")):
            # 记录操作日志
            await OperatorAuditRecord.create(
                username=username,
                request_url=request.url.path,
                request_method=request_method.upper(),
                request_body=json.dumps(request_body),
                response_code=response.status_code,
                response_content=response_body[0].decode(),
                process_time=float(round(process_time, 5)),
            )

        return response
