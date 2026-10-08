# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

头条新闻 App 的后端服务(FastAPI 教学项目),为前端提供用户、新闻、收藏三类接口。全异步技术栈:FastAPI + SQLAlchemy 2.0 async + MySQL(aiomysql)。代码注释为中文,按教学流程编号书写。

## 常用命令

项目暂无 requirements.txt、测试和 lint 配置。开发环境用 conda 管理(见 .vscode/settings.json),依赖包括:fastapi、uvicorn、sqlalchemy、aiomysql、pydantic、passlib、bcrypt。

启动开发服务器(标准方式):

```bash
uvicorn main:app --reload
```

## 架构

分层结构:routers(路由、参数校验、依赖注入)→ crud(数据库操作封装)→ models(SQLAlchemy ORM 模型);schemas 定义 Pydantic 请求/响应模型;utils 放横切工具(auth、security、response、exception)。

- **数据库会话**:连接串硬编码在 config/db_config.py(MySQL 的 news_app 库,root 用户)。建表不在此项目中完成(没有 create_all 也没有 alembic 迁移)。`get_db` 依赖负责 yield 会话、结束时 commit、异常时 rollback;注意 crud 层函数也会手动 commit,重复提交无害但要留意这个模式。
- **认证**:不是 JWT。token 是 uuid4 字符串,存在 user_token 表(有效期 7 天),前端通过 `Authorization: Bearer <token>` 头传入,`get_current_user`(utils/auth.py)作为依赖注入完成鉴权。密码用 passlib bcrypt 哈希(utils/security.py)。
- **响应约定**:统一为 `{code, message, data}`。成功响应走 utils/response.py 的 `success_response`;但 routers/news.py 直接手写 dict(结构相同),这是已知的不一致。
- **字段命名**:前端使用驼峰别名(categoryId、pageSize、hasMore、newsId、publishTime、isFavorite 等),schemas 里通过 `Field(alias=...)` 映射,写新接口时保持这个约定。
- **全局异常处理**:main.py 调用 `register_handle_exception(app)` 注册四级处理器(HTTPException → IntegrityError → SQLAlchemyError → Exception 兜底)。utils/exception.py 中 `DEBUG_MODE = True` 时响应里附带 traceback 详情,生产前应关闭。
- **Pydantic 版本**:代码使用 Pydantic v1 风格的 API(`orm_mode = True`、`from_orm()`、`.dict()`),升级到 v2 语法前需整体迁移,不要混写。
- **模型基类**:SQLAlchemy 2.0 风格的 `Mapped`/`mapped_column`,但 users/news/favorite 三个 models 文件各自声明了自己的 `Base`,没有统一基类,新增模型时沿用所在文件的写法即可。

接口前缀:/api/user、/api/news、/api/favorite(对应 routers/ 下的 users.py、news.py、favourite.py,注意 favourite 是英式拼写)。
