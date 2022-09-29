import binascii
import os
from datetime import datetime, timedelta
from typing import Any, Union

from app.models.rbac import User
from common.exceptions import UnauthorisedException
from config.setting import settings
from fastapi import Depends, Request, WebSocket, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError


def check_token(
    auth_token: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(
            scheme_name="bearerAuth",
            bearerFormat="JWT",
            auto_error=False,
        )
    )
) -> str:
    """
    Check valid token
    :param auth_token:
    :return: str
    """
    if auth_token is None:
        raise UnauthorisedException("missing token")

    try:
        payload = jwt.decode(auth_token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id: str = payload.get("sub")
        if user_id is None:
            raise JWTError
    except JWTError:
        raise UnauthorisedException("Access token is invalid")
    return user_id


async def get_current_user(user_id: str = Depends(check_token)) -> User:
    """
    Fetch logged in user from database
    :param user_id:
    :return: User
    """
    user = await User.find_by_id(_id=user_id)
    if user is None:
        raise UnauthorisedException("Access token is invalid")
    return user


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    生成access_token
    :param subject:需要存储到token的数据
    :param expires_delta:过期时间
    :return:
    """
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_DELTA)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(n: int = 24) -> str:
    """
    生成refresh_token
    :param n:
    :return:
    """
    return str(binascii.hexlify(os.urandom(n)), "utf-8")


async def get_current_username(request: Request) -> str:
    try:
        username = request.app.state.username
    except Exception:
        try:
            bear = HTTPBearer(
                scheme_name="bearerAuth",
                bearerFormat="JWT",
                auto_error=False,
            )
            auth_token: HTTPAuthorizationCredentials = await bear(request=request)  # type: ignore
            payload = jwt.decode(auth_token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            user_id: str = payload.get("sub")
            user = await User.find_by_id(_id=user_id)
            username = user.username
        except Exception:
            raise UnauthorisedException("Access token is invalid")
    return username


async def check_token_from_query(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> str:
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id: str = payload.get("sub")
        user = await User.find_by_id(_id=user_id)
        username = user.username
        return username
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return ""
