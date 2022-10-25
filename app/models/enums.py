from enum import IntEnum, Enum


class Status(IntEnum):
    ENABLE = 0
    DISABLE = 1


class HostType(str, Enum):
    IDC = "idc"
    CLOUD = "cloud"
    LOCAL = "local"


class BelongsTo(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    HUAWEI = "huawei"
    ALIYUN = "aliyun"
    TENCENT = "tencent"
    JINSHAN = "jinshan"
    UCLOUD = "ucloud"
    BAIDU = "baidu"
    JINGDONG = "jingdong"
    QINIU = "qiniu"
    IDC = "idc"
    LOCAL = "local"


class DiskType(str, Enum):
    SSD = "SSD"
    HDD = "HDD"


class DbType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "pg"
    MARIADB = "maria"
    MONGODB = "mongo"
    REDIS = "redis"
    ELASTICSEARCH = "elastic"
    HBASE = "hbase"


class DbSource(str, Enum):
    HOST = "host"
    CLOUD = "cloud"


class ConfigCenterType(str, Enum):
    NACOS = "nacos"
    POLARIS = "polaris"
    APOLLO = "apollo"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ExecCommand(str, Enum):
    SHELL = "shell"
    PYTHON2 = "py2"
    PYTHON3 = "py3"
    GO = "go"
    ANSIBLE = "ansible"


class ScriptType(str, Enum):
    GROUP = "group"
    NODE = "node"


class SSHStatus(IntEnum):
    ONLINE = 0
    OFFLINE = 1


class DeployConfigType(str, Enum):
    DOCKER_REGISTRY = "docker_registry"
    K8S = "k8s"
    GIT = "git"


class ApplicationLanguage(str, Enum):
    PYTHON = "python"
    GO = "go"
    JAVA = "java"
    C = "c"
    CPLUSPLUS = "c++"
    LUA = "lua"
    JAVASCRIPT = "js"
    TYPESCRIPT = "ts"
    CSHARP = "c#"
    PHP = "php"
