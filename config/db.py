from typing import Dict

from config.setting import settings

# TORTOISE_ORM配置
TORTOISE_ORM: Dict = {
    "connections": {"default": settings.DB_ADDRESS},
    "apps": {
        "models": {
            "models": [
                "app.models.rbac",
                "app.models.cmdb",
                "app.models.audit",
                "app.models.job",
                "app.models.wiki",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
