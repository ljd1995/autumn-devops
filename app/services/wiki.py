from typing import List, Type

import aiofiles  # type: ignore
from anyio import Path
from app.models.wiki import WikiCategory
from app.schemas.model_creator import WikiCategoryModel
from app.schemas.wiki import WikiCategoryPageQuerySchema
from app.services.children import ChildService
from fastapi import UploadFile
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from utils.crypt import md5_encode_with_salt


class WikiCategoryService(object):
    @staticmethod
    async def get_children_data_with_page(param: WikiCategoryPageQuerySchema) -> List:
        async def _get_children_data(obj: Model, model_pydantic: Type[PydanticModel]) -> dict:
            childrens = await obj.children.filter(zone_id=param.zone_id)  # type: ignore
            ret = await model_pydantic.from_tortoise_orm(obj)
            result = ret.dict()
            children_list = []
            for children in childrens:
                ret = await _get_children_data(children, model_pydantic)
                children_list.append(ret)
            wiki_page_obj_qs = await obj.pages.all()  # type: ignore
            pages_data = []
            for page_obj in wiki_page_obj_qs:
                item = {
                    "key": f"page-{page_obj.id}",
                    "id": f"page-{page_obj.id}",
                    # Ant-Design-Vue3 Tree组件会校验KEY，KEY如果重复会导致展示异常，故key加前缀来避免
                    "title": page_obj.name,
                    "name": page_obj.name,
                    "is_page": True,
                    "page_id": page_obj.id,
                    "remark": page_obj.remark,
                    "content": page_obj.content,
                    "secret": page_obj.secret,
                    "parent_id": page_obj.wiki_category_id,
                }
                pages_data.append(item)
            if pages_data and children_list == []:
                children_list = pages_data
            result["children"] = children_list
            return result

        root_obj = await WikiCategory.get_or_create(name="根")
        wiki_category_obj_qs = await WikiCategory.filter(zone_id=param.zone_id)
        wiki_category_obj_qs.append(root_obj[0])
        data = await ChildService.get_children_data(
            wiki_category_obj_qs, WikiCategoryModel, children_handler=_get_children_data
        )
        return data


class WikiPageService(object):
    @staticmethod
    async def upload_file(file: UploadFile) -> str:
        base_dir = Path(__file__).parent.parent.parent
        file_name_md5 = md5_encode_with_salt(file.filename)
        file_suffix = file.filename.split(".")[-1]
        file_path = f"{file_name_md5}.{file_suffix}" if file_suffix else file_name_md5
        async with aiofiles.open(base_dir / "uploads" / file_path, "wb") as f:
            await f.write(file.file.read())
        download_url = f"/api/v1/uploads/{file_path}"
        return download_url
