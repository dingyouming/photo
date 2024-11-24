from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from photo_app.core.models.photo import Photo, PhotoMetadata
from photo_app.core.models.tag import Tag
from photo_app.core.models.album import Album
from photo_app.core.dao.base import BaseDAO

class PhotoDAO(BaseDAO[Photo]):
    """照片数据访问对象，实现照片相关的所有数据库操作"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Photo)

    async def get_with_metadata(self, photo_id: int) -> Optional[Photo]:
        """获取照片及其元数据"""
        stmt = (
            select(Photo)
            .options(selectinload(Photo.photo_metadata))
            .where(Photo.id == photo_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
        include_metadata: bool = False
    ) -> List[Photo]:
        """获取用户的照片列表"""
        stmt = (
            select(Photo)
            .where(Photo.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Photo.upload_date.desc())
        )
        
        if include_metadata:
            stmt = stmt.options(selectinload(Photo.photo_metadata))
            
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self,
        user_id: int,
        *,
        tags: Optional[List[str]] = None,
        album_id: Optional[int] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        filename: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Photo]:
        """高级搜索功能"""
        conditions = [Photo.user_id == user_id]
        
        if tags:
            tag_condition = Photo.tags.any(Tag.name.in_(tags))
            conditions.append(tag_condition)
            
        if album_id:
            album_condition = Photo.albums.any(Album.id == album_id)
            conditions.append(album_condition)
            
        if date_range:
            start_date, end_date = date_range
            date_condition = and_(
                Photo.upload_date >= start_date,
                Photo.upload_date <= end_date
            )
            conditions.append(date_condition)
            
        if filename:
            filename_condition = Photo.filename.ilike(f"%{filename}%")
            conditions.append(filename_condition)

        stmt = (
            select(Photo)
            .where(and_(*conditions))
            .options(selectinload(Photo.tags))
            .offset(skip)
            .limit(limit)
            .order_by(Photo.upload_date.desc())
        )
        
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_storage_stats(self, user_id: int) -> dict:
        """获取存储统计信息"""
        stmt = (
            select(
                func.count(Photo.id).label("total_photos"),
                func.sum(Photo.size).label("total_size"),
                func.avg(Photo.size).label("avg_size")
            )
            .where(Photo.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        row = result.one()
        return {
            "total_photos": row.total_photos or 0,
            "total_size": row.total_size or 0,
            "avg_size": row.avg_size or 0
        }

    async def get_backup_candidates(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Photo]:
        """获取需要备份的照片"""
        stmt = (
            select(Photo)
            .where(
                and_(
                    Photo.user_id == user_id,
                    Photo.backup_status == "pending",
                    Photo.storage_status == "completed"
                )
            )
            .limit(limit)
            .order_by(Photo.upload_date.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_storage_status(
        self,
        photo_id: int,
        status: str,
        failure_reason: Optional[str] = None
    ) -> bool:
        """更新存储状态"""
        update_data = {
            "storage_status": status,
            "failure_reason": failure_reason
        }
        if status == "failed" and failure_reason:
            update_data["retry_count"] = Photo.retry_count + 1
            
        return await self.update(photo_id, **update_data) is not None

    async def get_by_tag(self, tag_name: str, user_id: int) -> List[Photo]:
        """获取指定标签的照片"""
        stmt = (
            select(Photo)
            .join(Photo.tags)
            .where(
                and_(
                    Photo.user_id == user_id,
                    Tag.name == tag_name
                )
            )
            .options(selectinload(Photo.tags))
            .order_by(Photo.upload_date.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_photos_by_tag(
        self,
        user_id: int,
        tag_name: str,
        *,
        skip: int = 0,
        limit: int = 50
    ) -> List[Photo]:
        """获取指定标签的照片"""
        stmt = (
            select(Photo)
            .join(Photo.tags)
            .where(
                and_(
                    Photo.user_id == user_id,
                    Tag.name == tag_name
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Photo.upload_date.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
