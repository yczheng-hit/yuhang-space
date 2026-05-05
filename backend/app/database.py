"""异步 SQLAlchemy 引擎与会话工厂。"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    """获取异步数据库会话（用于 FastAPI 依赖注入）。"""
    async with async_session_factory() as session:
        yield session
