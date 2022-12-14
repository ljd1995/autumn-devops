from app.models.audit import OperatorAuditRecord, SSHAuditRecord
from app.models.basis import HostGroup, Host, Db, ConfigCenter, Application, Environment, EnvironmentGroup, DeployConfig
from app.models.cicd import Artifact, CICDPlugin, PipelinePlugin
from app.models.job import AdhocHistory, Script
from app.models.rbac import User, Department, Role
from app.models.wiki import WikiZone, WikiCategory, WikiPage
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

# Initialize model relationships
Tortoise.init_models(
    ["app.models.rbac", "app.models.basis", "app.models.audit", "app.models.job", "app.models.wiki"], "models"
)

# RBAC
UserModel = pydantic_model_creator(User, name="UserModel")
DepartmentModel = pydantic_model_creator(Department, name="DepartmentModel")
RoleModel = pydantic_model_creator(Role, name="RoleModel")
UserReq = pydantic_model_creator(User, name="UserReq", exclude=("id", "create_time", "update_time", "last_login_time"))
DepartmentReq = pydantic_model_creator(Department, name="DepartmentReq", exclude=("id", "create_time", "update_time"))
RoleReq = pydantic_model_creator(Role, name="RoleReq", exclude=("id", "create_time", "update_time"))

# BASIS
HostModel = pydantic_model_creator(Host, name="HostModel")
HostGroupModel = pydantic_model_creator(HostGroup, name="HostGroupModel", computed=("key", "title"))
HostReq = pydantic_model_creator(
    Host,
    name="HostReq",
    include=(
        "intranet_ip",
        "external_ip",
        "host_type",
        "belongs_to",
        "login_user",
        "password",
        "port",
        "remark",
        "host_group_id",
        "proxy_ips",
    ),
)
HostGroupReq = pydantic_model_creator(
    HostGroup,
    name="HostGroupReq",
    include=("name", "parent_id", "remark"),
)
DbModel = pydantic_model_creator(Db, name="DbModel")
DbReq = pydantic_model_creator(Db, name="DbReq", exclude=("id", "create_time", "update_time"))
ConfigCenterModel = pydantic_model_creator(ConfigCenter, name="ConfigCenterModel")
ConfigCenterReq = pydantic_model_creator(
    ConfigCenter, name="ConfigCenterReq", exclude=("id", "create_time", "update_time")
)
ApplicationModel = pydantic_model_creator(Application, name="ApplicationModel")
ApplicationBaseReq = pydantic_model_creator(
    Application,
    name="ApplicationBaseReq",
    exclude=("id", "create_time", "update_time", "create_user", "update_user", "application_groups"),
)
EnvironmentModel = pydantic_model_creator(Environment, name="EnvironmentModel")
EnvironmentReq = pydantic_model_creator(
    Environment, name="EnvironmentReq", exclude=("id", "create_time", "update_time")
)
EnvironmentGroupModel = pydantic_model_creator(EnvironmentGroup, name="EnvironmentGroupModel")

EnvironmentGroupReq = pydantic_model_creator(
    EnvironmentGroup,
    name="EnvironmentGroupReq",
    exclude=("id", "create_time", "update_time", "env_name", "db_name", "config_name"),
)
DeployConfigModel = pydantic_model_creator(DeployConfig, name="DeployConfigModel")
DeployConfigReq = pydantic_model_creator(
    DeployConfig,
    name="DeployConfigReq",
    exclude=("id", "create_time", "update_time"),
)

# AUDIT
OperatorAuditRecordModel = pydantic_model_creator(OperatorAuditRecord, name="OperatorAuditRecordModel")
OperatorAuditRecordReq = pydantic_model_creator(
    OperatorAuditRecord,
    name="OperatorAuditRecordReq",
    exclude=("id", "create_time", "update_time", "request_time", "process_time"),
)
SSHAuditRecordModel = pydantic_model_creator(SSHAuditRecord, name="SSHAuditRecordModel")
SSHAuditRecordReq = pydantic_model_creator(
    SSHAuditRecord,
    name="SSHAuditRecordReq",
    exclude=(
        "id",
        "create_time",
        "update_time",
    ),
)

# Job
AdhocHistoryModel = pydantic_model_creator(AdhocHistory, name="AdhocHistoryModel")
AdhocHistoryReq = pydantic_model_creator(
    AdhocHistory,
    name="AdhocHistoryReq",
    exclude=(
        "id",
        "create_time",
        "update_time",
    ),
)
ScriptModel = pydantic_model_creator(Script, name="ScriptModel", computed=("key", "title"))
ScriptReq = pydantic_model_creator(
    Script,
    name="ScriptReq",
    exclude=("id", "create_time", "update_time", "children", "script_history"),
)

# Wiki
WikiZoneModel = pydantic_model_creator(WikiZone, name="WikiZoneModel")
WikiZoneReq = pydantic_model_creator(
    WikiZone,
    name="WikiZoneReq",
    exclude=(
        "id",
        "create_time",
        "update_time",
    ),
)
WikiCategoryModel = pydantic_model_creator(WikiCategory, name="WikiCategoryModel", computed=("key", "title"))
WikiCategoryReq = pydantic_model_creator(
    WikiCategory,
    name="WikiCategoryReq",
    exclude=("id", "create_time", "update_time", "children"),
)
WikiPageModel = pydantic_model_creator(WikiPage, name="WikiPageModel")
WikiPageReq = pydantic_model_creator(
    WikiPage,
    name="WikiPageReq",
    exclude=("id", "create_time", "update_time", "create_user", "update_user"),
)

# CICD
ArtifactModel = pydantic_model_creator(Artifact, name="ArtifactModel")
ArtifactBaseReq = pydantic_model_creator(
    Artifact,
    name="ArtifactReq",
    exclude=("id", "create_time", "update_time", "create_user", "update_user"),
)
CICDPluginModel = pydantic_model_creator(CICDPlugin, name="CICDPluginModel")
CICDPluginReq = pydantic_model_creator(
    CICDPlugin,
    name="CICDPluginReq",
    exclude=("id", "create_time", "update_time"),
)
PipelinePluginReq = pydantic_model_creator(
    PipelinePlugin,
    name="PipelinePluginReq",
    exclude=("id", "create_time", "update_time"),
)
