autumn 是一个前端基于Vue3.2 、Vite2.9.5、 Ant-Design-Vue3.2 、TypeScript, 后端基于Python3.10 FastAPI 框架开发的一站式DevOps解决方案,
目标是为中小型公司提供现成的DevOps管理平台。

## 安装前

项目基于Python 3.10最新语法开发，请确保使用的Python版本符合要求

## 安装

**依赖管理工具**

项目基于[pdm](https://pdm.fming.dev/latest/)
管理项目依赖，pdm作者是国人，也是pipenv的开发者之一，相对于pipenv、poetry这类python依赖管理工具，pdm支持virtualenv、PEP
582两种模式，更加先进更好用，可用以下方式安装

```bash
pip install pdm
```

**安装项目依赖**

```bash
pdm install
```

**修改数据库配置**

```ini
    # config/setting.py

    # 数据库地址
    DB_ADDRESS: str = "mysql://root:123456@127.0.0.1:3306/autumn"

    # Redis Host
    REDIS_HOST: str = "127.0.0.1"
    # Redis Port
    REDIS_PORT: int = 6379
    # Redis database
    REDIS_DB: int = 0
```

**执行数据库迁移**

```bash
pdm run aerich init -t config.db.TORTOISE_ORM
pdm run aerich init-db
```

**执行预SQL**

```sql
INSERT INTO `autumn`.`t_wiki_category` (`id`, `name`, `remark`, `parent_id`, `zone_id`)
VALUES (1, '根', '', NULL, NULL);
INSERT INTO `autumn`.`t_script` (`id`, `name`, `content`, `exec_command`, `remark`, `node_type`, `create_user`,
                                 `update_user`, `parent_id`)
VALUES (1, '根', '', 'shell', '', 'group', '', '', NULL);
INSERT INTO `autumn`.`t_host_group` (`id`, `name`, `remark`, `parent_id`)
VALUES (1, '根', '', NULL);
```

**启动程序**

```bash
pdm run uvicorn main:app
```

## 功能
