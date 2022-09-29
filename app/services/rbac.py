from typing import Tuple, List, Dict

from app.models.rbac import User, Department
from app.schemas.auth import LoginReq
from app.schemas.model_creator import UserModel, DepartmentModel
from app.schemas.rbac import DepartmentChildrenQuerySchema, UserModifyPasswordReq
from app.services.children import ChildService
from common.exceptions import APIException
from tortoise.contrib.pydantic import PydanticModel
from tortoise.models import MODEL
from tortoise.queryset import QuerySet


class UserService(object):
    @staticmethod
    async def validate_login(param: LoginReq) -> Tuple[bool, User | None]:
        if not (user := await User.filter(username=param.username).first()):
            return False, None
        if user.verify_hash(param.password, user.password):
            return True, user
        return False, User()

    @staticmethod
    async def get_user_info(user: User) -> PydanticModel:
        data = await UserModel.from_tortoise_orm(user)
        return data

    @staticmethod
    async def modify_user_password(param: UserModifyPasswordReq) -> None:
        if not (user := await User.filter(username=param.username).first()):
            raise APIException("This user does not exist.")
        if user.verify_hash(param.password_old, user.password):
            user.password = user.generate_hash(param.password_new)
            await user.save()
        else:
            raise APIException("This user password is incorrect.")

    @staticmethod
    async def get_page_queryset(queryset: QuerySet[MODEL], item: Dict) -> QuerySet[MODEL]:
        if "department_id" in item:
            users = await queryset.filter(department_id=item["department_id"])
            if not users:
                department_id = item.pop("department_id")
                department_obj = await Department.get(pk=department_id)
                children = await department_obj.children.all()
                children_ids = [child.id for child in children]
                queryset = queryset.filter(department_id__in=children_ids).filter(**item)
                return queryset
            else:
                return queryset.filter(**item)
        else:
            return queryset.filter(**item)


class DepartmentService(object):
    @staticmethod
    async def get_children_data(param: DepartmentChildrenQuerySchema) -> List:
        query = param.dict(exclude_unset=True, exclude_none=True)
        search_value = query.pop("search", None)
        if query:
            department_obj_qs = await Department.fuzzy_search(search_value=search_value).filter(**query)
        else:
            department_obj_qs = await Department.fuzzy_search(search_value=search_value)
        data = await ChildService.get_children_data(department_obj_qs, DepartmentModel)

        return data
