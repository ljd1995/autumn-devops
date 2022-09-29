from enum import Enum
from typing import Dict, List

from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel


class TypeEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ResponseSchema(BaseModel):
    code: int
    message: str
    result: List | Dict | str | PydanticModel | BaseModel | None = None
    type: TypeEnum = TypeEnum.SUCCESS
