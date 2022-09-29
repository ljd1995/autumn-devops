from app.schemas.resp import ResponseSchema
from pydantic import BaseModel


class LoginReq(BaseModel):
    username: str
    password: str


class LoginResp(BaseModel):
    access_token: str
    refresh_token: str


class NewTokenReq(BaseModel):
    refresh_token: str


class NewTokenResp(BaseModel):
    access_token: str


class LoginRespSchema(ResponseSchema):
    result: LoginResp | None


class NewTokenRespSchema(ResponseSchema):
    result: NewTokenResp | None
