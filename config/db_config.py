from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
URL = "mysql+aiomysql://root:20001211@localhost:3306/news_app?utf8mb4"
#创建异步引擎
async_engine  = create_async_engine(
    URL,
    echo = True,
    pool_size = 10,
    max_overflow = 20
)

#创建异步会话工厂
session =  async_sessionmaker(
    bind = async_engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

#依赖项，获取数据库会话
async def get_db():
    async with session() as db_session:
        try:
            yield db_session
            await db_session.commit()  # 接口业务正常走完，提交事务
        except Exception:
            await db_session.rollback() # 出现任何异常，回滚事务
            raise   # 继续把异常抛出去给FastAPI处理
        finally:
            await db_session.close() #