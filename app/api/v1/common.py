from app.schemas.resp import ResponseSchema
from app.services.common import DependenciesService
from common import resp
from fastapi.routing import APIRouter, Response

router = APIRouter(tags=["通用"])


@router.get("/common/dependencies", response_model=ResponseSchema, summary="获取项目所有依赖")
async def get_dependencies() -> Response:
    data = await DependenciesService.get_dependencies()
    return resp.ok(data=data)
