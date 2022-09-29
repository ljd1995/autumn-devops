from app.models.rbac import User
from app.schemas.auth import (
    LoginReq,
    LoginRespSchema,
    NewTokenRespSchema,
    NewTokenReq,
    LoginResp,
    NewTokenResp,
)
from app.schemas.rbac import UserRespSchema
from app.schemas.resp import ResponseSchema
from app.services.auth import AuthService
from app.services.rbac import UserService
from common import resp
from core.security import get_current_user, check_token
from fastapi import Depends, APIRouter, Response, Request

router = APIRouter(tags=["鉴权"])


@router.post("/token", response_model=LoginRespSchema, summary="获取用户访问token")
async def user_login(*, body: LoginReq, request: Request) -> Response:
    access_token, refresh_token = await AuthService.authenticate(body)
    request.app.state.username = body.username
    return resp.ok(data=LoginResp(access_token=access_token, refresh_token=refresh_token))


@router.get("/token/me", summary="获取用户详情", response_model=UserRespSchema)
async def get_user_info(*, current_user: User = Depends(get_current_user)) -> Response:
    data = await UserService.get_user_info(current_user)
    return resp.ok(data=data)


@router.post("/token/refresh", response_model=NewTokenRespSchema, summary="刷新用户访问token")
async def get_new_token(*, body: NewTokenReq, user_id: str = Depends(check_token)) -> Response:
    access_token = await AuthService.generate_new_access_token(user_id, body.refresh_token)
    return resp.ok(data=NewTokenResp(access_token=access_token))


@router.delete("/token", response_model=ResponseSchema, summary="退出登录")
async def delete(*, user_id: str = Depends(check_token)) -> Response:
    await AuthService.logout(user_id)
    return resp.ok(data=None)
