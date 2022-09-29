from datetime import timedelta
from typing import Tuple

from app.models.enums import Status
from app.schemas.auth import LoginReq
from app.services.rbac import UserService
from common.exceptions import UnauthorisedException, AuthenticationFailedException
from common.redis import redis_client
from config.setting import settings
from core import security


class AuthService(object):
    @classmethod
    async def authenticate(cls, param: LoginReq) -> Tuple[str, str]:
        ok, user = await UserService.validate_login(param)

        if not ok:
            raise UnauthorisedException("user or password is incorrect.")

        if user.status == Status.DISABLE:  # type: ignore
            raise UnauthorisedException("the user has been disabled!")

        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_DELTA)

        access_token = security.create_access_token(user.id, expires_delta=access_token_expires)  # type: ignore
        refresh_token = security.create_refresh_token()

        # 持久化 refresh_token
        await cls.store_refresh_token(user.id, refresh_token)  # type: ignore

        return access_token, refresh_token

    @classmethod
    async def logout(cls, user_id: str) -> None:
        await cls.delete_refresh_token(user_id)

    @classmethod
    async def generate_new_access_token(cls, user_id: str, token: str) -> str:
        refresh_token = await cls.retrieve_refresh_token(user_id)

        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode("utf-8")

        if refresh_token != token:
            raise AuthenticationFailedException("refresh token not valid!")

        # 生成新的 access_token
        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_DELTA)
        access_token = security.create_access_token(user_id, expires_delta=access_token_expires)

        return access_token

    @staticmethod
    async def store_refresh_token(user_id: str, refresh_token: str) -> None:
        """使用 Redis 存储 refresh_token, 并设置过期时间"""
        key = f"refresh_token_{user_id}"
        await redis_client.setex(key, settings.REFRESH_TOKEN_EXPIRE_DELTA, refresh_token)

    @staticmethod
    async def retrieve_refresh_token(user_id: str) -> str:
        key = f"refresh_token_{user_id}"
        token = await redis_client.get(key)
        if not token:
            raise UnauthorisedException("can not find refresh token")
        return token

    @staticmethod
    async def delete_refresh_token(user_id: str) -> None:
        key = f"refresh_token_{user_id}"
        await redis_client.delete(key)
