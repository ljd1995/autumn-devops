from app.api.base import BaseRouter
from app.models.audit import OperatorAuditRecord, SSHAuditRecord
from app.schemas.audit import (
    OperatorAuditRecordRespSchema,
    OperatorAuditRecordQuerySchema,
    SSHAuditRecordRespSchema,
    SSHAuditRecordQuerySchema,
)
from app.schemas.model_creator import OperatorAuditRecordReq, SSHAuditRecordReq

operator_audit_router = BaseRouter(
    model=OperatorAuditRecord,
    tag_name="审计",
    model_name="请求操作审计",
    request_schema=OperatorAuditRecordReq,
    response_schema=OperatorAuditRecordRespSchema,
    query_schema=OperatorAuditRecordQuerySchema,
    model_path="audit/operator-history",
)

ssh_audit_router = BaseRouter(
    model=SSHAuditRecord,
    tag_name="审计",
    model_name="SSH操作审计",
    request_schema=SSHAuditRecordReq,
    response_schema=SSHAuditRecordRespSchema,
    query_schema=SSHAuditRecordQuerySchema,
    model_path="audit/ssh-history",
)


operator_audit_router.load_crud_routes(
    only_paginate=True,
)

ssh_audit_router.load_crud_routes(
    only_paginate=True,
)
