<div align=center>

![](images/logo.png)

![](https://img.shields.io/github/license/ljd1995/autumn-devops)
![](https://img.shields.io/badge/python-3.10-blue)
![](https://img.shields.io/github/last-commit/ljd1995/autumn-devops/master)
</div>

目录
=================

* [前言](#前言)
* [要求](#要求)
* [安装](#安装)
* [页面展示](#页面展示)
* [功能](#功能)
* [License](#license)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->

## 前言

autumn 是一个前端基于Vue3.2 、Vite2.9.5、 Ant-Design-Vue3.2 、TypeScript, 后端基于Python3.10 FastAPI 框架开发的一站式DevOps解决方案,
目标是为中小型公司提供现成的DevOps管理平台。

前端：https://github.com/ljd1995/autumn-devops-web

后端：https://github.com/ljd1995/autumn-devops

## 要求

项目基于Python 3.10最新语法开发，请确保使用的Python版本符合要求

## 安装

- 依赖管理工具

项目基于[pdm](https://pdm.fming.dev/latest/)
管理项目依赖，pdm作者是国人，也是pipenv的开发者之一，相对于pipenv、poetry这类python依赖管理工具，pdm支持virtualenv、PEP
582两种模式，更加先进更好用，可用以下方式安装

```bash
pip install pdm
```

- 安装项目依赖

```bash
pdm install
```

- 修改数据库配置

```python
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

- 执行数据库迁移

```bash
pdm run aerich init -t config.db.TORTOISE_ORM
pdm run aerich init-db
```

- 执行预SQL

```sql
INSERT INTO `autumn`.`t_wiki_category` (`id`, `name`, `remark`, `parent_id`, `zone_id`)
VALUES (1, '根', '', NULL, NULL);
INSERT INTO `autumn`.`t_script` (`id`, `name`, `content`, `exec_command`, `remark`, `node_type`, `create_user`,
                                 `update_user`, `parent_id`)
VALUES (1, '根', '', 'shell', '', 'group', '', '', NULL);
INSERT INTO `autumn`.`t_host_group` (`id`, `name`, `remark`, `parent_id`)
VALUES (1, '根', '', NULL);
```

- 启动程序

```bash
pdm run uvicorn main:app
```

## 页面展示

![host_manage](./images/host_manage.png)

![database_list](./images/database_list.png)

![web_terminal](./images/web_terminal.png)

![db_column](./images/db_column.png)

![db_query](./images/db_query.png)

![adhoc](./images/adhoc.png)

![playbook](./images/playbook.png)

![script_manage](./images/script_manage.png)

![script_history](./images/script_history.png)

![script_compare](./images/script_compare.png)

![wiki_zone](./images/wiki_zone.png)

![wiki_category_page](./images/wiki_category_page.png)

![wiki_page](./images/wiki_page.png)

![request_audit](./images/request_audit.png)

![ssh_audit](./images/ssh_audit.png)

![user_manage](./images/user_manage.png)

![role_manage](./images/role_manage.png)

![department_manage](./images/department_manage.png)

![modify_password](./images/modify_password.png)

## 功能

- [x] RBAC
    - [x] 用户管理
        - [x] 账号密码登录
        - [ ] 钉钉登录
        - [ ] 企业微信登录
        - [ ] 飞书登录
        - [ ] 禅道登录
    - [x] 角色管理
    - [x] 部门管理
    - [ ] 菜单管理
    - [ ] 权限管理
- [x] CMDB
    - [x] 资产管理
    - [x] 数据库管理
    - [x] 配置中心管理
- [x] 作业平台
    - [x] adhoc执行
    - [x] 脚本管理
    - [x] 脚本执行
- [x] wiki知识库
    - [x] wiki空间
    - [x] wiki目录
    - [x] wiki页面(markdown编辑、页面带密码分享)
- [x] 操作审计
    - [x] 请求审计
    - [x] SSH操作审计
- [x] Web工具
    - [x] Web Terminal
    - [x] Web数据库管理
- [ ] CI/CD
    - [ ] 组合式流水线
    - [ ] 制品仓库
    - [ ] 多配置中心支持
    - [ ] 多编译环境支持
    - [ ] 多部署环境支持
    - [ ] 云原生与传统方式部署支持
    - [ ] 代码扫描
    - [ ] 镜像扫描
    - [ ] 代码库管理
    - [ ] Webhook
- [ ] 监控管理
- [ ] 工单管理
- [ ] 变更与审批管理
- [ ] 稳定性保障

## License

[MIT © autumn-devops-2022](./LICENSE)