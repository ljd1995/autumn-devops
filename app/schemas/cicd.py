from typing import List

from app.schemas.paginate import BasePageSchema
from app.schemas.resp import ResponseSchema
from pydantic import BaseModel
from .model_creator import ArtifactModel, CICDPluginModel, ArtifactBaseReq, PipelinePluginReq


class ArtifactRespSchema(ResponseSchema):
    result: ArtifactModel | None  # type: ignore


class ArtifactQuerySchema(BasePageSchema):
    ...


class PipelineReq(BaseModel):
    name: str
    remark: str
    environment_id: int | str
    application_id: int | str
    plugins: List[PipelinePluginReq]  # type: ignore


class ArtifactReq(ArtifactBaseReq):  # type: ignore
    pipelines: List[PipelineReq] | None


class CICDPluginRespSchema(ResponseSchema):
    result: CICDPluginModel | None  # type: ignore


class CICDPluginQuerySchema(BasePageSchema):
    ...
