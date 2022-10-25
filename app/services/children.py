from typing import List, Dict, Type, Callable

from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel


class ChildService(object):
    @classmethod
    async def _get_children_data(cls, obj: Model, model_pydantic: Type[PydanticModel]) -> Dict:
        childrens = await obj.children.all()  # type: ignore
        ret = await model_pydantic.from_tortoise_orm(obj)
        result = ret.dict()
        children_list = []
        for children in childrens:
            ret = await cls._get_children_data(children, model_pydantic)  # type: ignore
            children_list.append(ret)
        result["children"] = children_list
        return result

    @classmethod
    async def get_children_data(
        cls, queryset: List[Model], model_pydantic: Type[PydanticModel], children_handler: Callable = None
    ) -> List:
        data = []
        for obj in queryset:
            if not obj.parent:  # type: ignore
                if children_handler:
                    item = await children_handler(obj, model_pydantic)
                else:
                    item = await cls._get_children_data(obj, model_pydantic)
                data.append(item)
        return data
