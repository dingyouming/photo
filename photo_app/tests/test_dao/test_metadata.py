import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from photo_app.core.dao.metadata import PhotoMetadataDAO
from photo_app.core.models.photo import PhotoMetadata

@pytest.mark.asyncio
class TestPhotoMetadataDAO:
    async def test_create_metadata(self, async_session: AsyncSession, sample_photo):
        dao = PhotoMetadataDAO(async_session)
        metadata = await dao.create(
            photo_id=sample_photo.id,
            scene_type="landscape",
            scene_confidence=0.95,
            faces_detected=2,
            face_locations="[[10, 10, 100, 100], [200, 200, 300, 300]]",
            aesthetic_score=8.5
        )
        
        assert metadata.id is not None
        assert metadata.photo_id == sample_photo.id
        assert metadata.scene_type == "landscape"
        assert metadata.faces_detected == 2

    async def test_get_by_photo_id(self, async_session: AsyncSession, sample_metadata):
        dao = PhotoMetadataDAO(async_session)
        metadata = await dao.get_by_photo_id(sample_metadata.photo_id)
        
        assert metadata is not None
        assert metadata.id == sample_metadata.id
        assert metadata.photo_id == sample_metadata.photo_id

    async def test_bulk_create(self, async_session: AsyncSession, test_user, sample_photo):
        dao = PhotoMetadataDAO(async_session)
        metadata_list = [
            {
                "photo_id": sample_photo.id,
                "scene_type": "landscape",
                "scene_confidence": 0.95,
                "aesthetic_score": 8.5
            },
            {
                "photo_id": sample_photo.id + 1,
                "scene_type": "portrait",
                "scene_confidence": 0.88,
                "faces_detected": 1
            }
        ]
        
        created = await dao.bulk_create(metadata_list)
        assert len(created) == 2
        assert all(isinstance(m, PhotoMetadata) for m in created)

    async def test_update_ai_analysis(self, async_session: AsyncSession, sample_metadata):
        dao = PhotoMetadataDAO(async_session)
        updated = await dao.update_ai_analysis(
            photo_id=sample_metadata.photo_id,
            scene_type="portrait",
            scene_confidence=0.92,
            faces_detected=1
        )
        
        assert updated is not None
        assert updated.scene_type == "portrait"
        assert updated.scene_confidence == 0.92
        assert updated.faces_detected == 1

    async def test_get_photos_by_scene(self, async_session: AsyncSession, sample_metadata_list):
        dao = PhotoMetadataDAO(async_session)
        results = await dao.get_photos_by_scene(
            scene_type="landscape",
            confidence_threshold=0.8
        )
        
        assert len(results) > 0
        assert all(m.scene_type == "landscape" for m in results)
        assert all(m.scene_confidence >= 0.8 for m in results)

    async def test_get_photos_with_faces(self, async_session: AsyncSession, sample_metadata_list):
        dao = PhotoMetadataDAO(async_session)
        results = await dao.get_photos_with_faces(min_faces=2)
        
        assert len(results) > 0
        assert all(m.faces_detected >= 2 for m in results)

    async def test_get_top_aesthetic_photos(self, async_session: AsyncSession, sample_metadata_list):
        dao = PhotoMetadataDAO(async_session)
        results = await dao.get_top_aesthetic_photos(limit=3)
        
        assert len(results) == 3
        scores = [m.aesthetic_score for m in results]
        assert scores == sorted(scores, reverse=True)

    async def test_get_metadata_stats(self, async_session: AsyncSession, sample_metadata_list):
        dao = PhotoMetadataDAO(async_session)
        stats = await dao.get_metadata_stats()
        
        assert stats["total_photos_analyzed"] > 0
        assert isinstance(stats["average_aesthetic_score"], float)
        assert isinstance(stats["average_faces_per_photo"], float)
        assert stats["total_scenes_analyzed"] > 0

@pytest.fixture
async def sample_metadata(async_session: AsyncSession, sample_photo) -> PhotoMetadata:
    dao = PhotoMetadataDAO(async_session)
    metadata = await dao.create(
        photo_id=sample_photo.id,
        scene_type="landscape",
        scene_confidence=0.95,
        faces_detected=0,
        aesthetic_score=7.5
    )
    await async_session.commit()
    return metadata

@pytest.fixture
async def sample_metadata_list(async_session: AsyncSession) -> list[PhotoMetadata]:
    dao = PhotoMetadataDAO(async_session)
    metadata_list = []
    
    scene_types = ["landscape", "portrait", "urban", "nature"]
    for i in range(10):
        metadata = await dao.create(
            photo_id=i + 1,
            scene_type=scene_types[i % len(scene_types)],
            scene_confidence=0.8 + (i * 0.02),
            faces_detected=i % 3,
            aesthetic_score=5.0 + (i * 0.5)
        )
        metadata_list.append(metadata)
    
    await async_session.commit()
    return metadata_list
