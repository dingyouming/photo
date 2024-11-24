from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from photo_app.core.models.photo import PhotoMetadata
from photo_app.core.dao.base import BaseDAO

class PhotoMetadataDAO(BaseDAO[PhotoMetadata]):
    """照片元数据数据访问对象"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PhotoMetadata)

    async def get_by_photo_id(self, photo_id: int) -> Optional[PhotoMetadata]:
        """通过照片ID获取元数据"""
        stmt = select(PhotoMetadata).where(PhotoMetadata.photo_id == photo_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def bulk_create(self, metadata_list: List[Dict[str, Any]]) -> List[PhotoMetadata]:
        """批量创建元数据记录"""
        instances = [PhotoMetadata(**data) for data in metadata_list]
        self._session.add_all(instances)
        await self._session.flush()
        return instances

    async def update_ai_analysis(
        self,
        photo_id: int,
        *,
        scene_type: Optional[str] = None,
        scene_confidence: Optional[float] = None,
        faces_detected: Optional[int] = None,
        face_locations: Optional[str] = None,
        aesthetic_score: Optional[float] = None
    ) -> Optional[PhotoMetadata]:
        """更新AI分析结果"""
        update_data = {
            k: v for k, v in {
                "scene_type": scene_type,
                "scene_confidence": scene_confidence,
                "faces_detected": faces_detected,
                "face_locations": face_locations,
                "aesthetic_score": aesthetic_score
            }.items() if v is not None
        }
        
        if not update_data:
            return None
            
        metadata = await self.get_by_photo_id(photo_id)
        if metadata:
            return await self.update(metadata.id, **update_data)
        return None

    async def get_photos_by_scene(
        self,
        scene_type: str,
        confidence_threshold: float = 0.7
    ) -> List[PhotoMetadata]:
        """获取特定场景类型的照片元数据"""
        stmt = (
            select(PhotoMetadata)
            .where(
                and_(
                    PhotoMetadata.scene_type == scene_type,
                    PhotoMetadata.scene_confidence >= confidence_threshold
                )
            )
            .order_by(PhotoMetadata.scene_confidence.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_photos_with_faces(
        self,
        min_faces: int = 1
    ) -> List[PhotoMetadata]:
        """获取包含人脸的照片元数据"""
        stmt = (
            select(PhotoMetadata)
            .where(PhotoMetadata.faces_detected >= min_faces)
            .order_by(PhotoMetadata.faces_detected.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_top_aesthetic_photos(
        self,
        limit: int = 10
    ) -> List[PhotoMetadata]:
        """获取美学评分最高的照片元数据"""
        stmt = (
            select(PhotoMetadata)
            .where(PhotoMetadata.aesthetic_score.isnot(None))
            .order_by(PhotoMetadata.aesthetic_score.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_metadata_stats(self) -> Dict[str, Any]:
        """获取元数据统计信息"""
        stmt = select(
            func.count(PhotoMetadata.id).label("total"),
            func.avg(PhotoMetadata.aesthetic_score).label("avg_aesthetic_score"),
            func.avg(PhotoMetadata.faces_detected).label("avg_faces"),
            func.count(PhotoMetadata.scene_type).label("scenes_analyzed")
        )
        result = await self._session.execute(stmt)
        row = result.one()
        return {
            "total_photos_analyzed": row.total,
            "average_aesthetic_score": float(row.avg_aesthetic_score) if row.avg_aesthetic_score else 0.0,
            "average_faces_per_photo": float(row.avg_faces) if row.avg_faces else 0.0,
            "total_scenes_analyzed": row.scenes_analyzed
        }
