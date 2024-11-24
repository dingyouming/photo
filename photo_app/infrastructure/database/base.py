"""数据库基础模块

本模块提供了数据库的基础设施，包括：
1. 数据库引擎配置
2. 数据库会话管理
3. 数据库初始化功能

主要组件：
- engine: 全局数据库引擎实例
- async_session: 异步会话工厂
- Base: SQLAlchemy声明性基类
- init_db: 数据库初始化函数
- get_db: 数据库会话获取函数

使用说明：
1. 应用启动时调用init_db()初始化数据库
2. 使用get_db()获取数据库会话进行操作
3. 可以通过提供custom_engine参数来使用自定义数据库引擎（主要用于测试）

注意事项：
- 所有数据库操作都是异步的
- 使用SQLAlchemy 2.0语法
- 支持SQLite数据库
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from photo_app.core.config import settings

# 根据配置选择数据库URL
if settings.DB_TYPE == "sqlite":
    DATABASE_URL = f"sqlite+aiosqlite:///{settings.DB_PATH}"
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )
else:
    DATABASE_URL = (
        f"oracle+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_SERVICE}"
    )
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_size=5,
        max_overflow=10,
    )

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def init_db(custom_engine=None) -> None:
    """Initialize the database.
    
    Args:
        custom_engine: Optional engine to use for initialization. If not provided,
                      the default engine will be used.
    """
    target_engine = custom_engine or engine
    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
