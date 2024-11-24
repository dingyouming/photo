from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from photo_app.core.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseDAO(Generic[ModelType]):
    """
    提供基础的数据访问操作的抽象基类
    实现了通用的CRUD操作和基本的查询功能
    """

    def __init__(self, session: AsyncSession, model_class: type[ModelType]):
        self._session = session
        self._model_class = model_class

    async def create(self, **kwargs) -> ModelType:
        """创建新记录"""
        instance = self._model_class(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def get(self, id: Any) -> Optional[ModelType]:
        """通过ID获取记录"""
        return await self._session.get(self._model_class, id)

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """获取多条记录，支持分页"""
        stmt = (
            select(self._model_class)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, id: Any, **kwargs
    ) -> Optional[ModelType]:
        """更新记录"""
        stmt = (
            update(self._model_class)
            .where(self._model_class.id == id)
            .values(**kwargs)
            .returning(self._model_class)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, id: Any) -> bool:
        """删除记录"""
        stmt = delete(self._model_class).where(
            self._model_class.id == id
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, id: Any) -> bool:
        """检查记录是否存在"""
        stmt = select(1).where(self._model_class.id == id)
        result = await self._session.execute(stmt)
        return result.scalar() is not None

    def _build_query(self) -> Select:
        """构建基础查询"""
        return select(self._model_class)
