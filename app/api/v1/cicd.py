from app.api.base import BaseRouter
from app.models.cicd import Artifact, CICDPlugin
from app.schemas.cicd import (
    ArtifactRespSchema,
    ArtifactQuerySchema,
    CICDPluginRespSchema,
    CICDPluginQuerySchema,
    ArtifactReq,
)
from app.schemas.model_creator import CICDPluginReq

artifact_router = BaseRouter(
    model=Artifact,
    tag_name="CICD",
    model_name="制品",
    request_schema=ArtifactReq,
    response_schema=ArtifactRespSchema,
    query_schema=ArtifactQuerySchema,
    model_path="cicd/artifact",
)

cicd_plugin_router = BaseRouter(
    model=CICDPlugin,
    tag_name="CICD",
    model_name="CICD插件",
    request_schema=CICDPluginReq,
    response_schema=CICDPluginRespSchema,
    query_schema=CICDPluginQuerySchema,
    model_path="cicd/plugin",
)

artifact_router.load_crud_routes()
cicd_plugin_router.load_crud_routes(only_paginate=True)
