import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from photo_app.core.dao.photo import PhotoDAO
from photo_app.core.models.photo import Photo
from photo_app.core.models.tag import Tag, photo_tags
from photo_app.core.models.album import Album

@pytest.mark.asyncio
class TestPhotoDAO:
    async def test_create_photo(self, async_session: AsyncSession, test_user):
        dao = PhotoDAO(async_session)
        photo = await dao.create(
            filename="test.jpg",
            filepath="/test/test.jpg",
            size=1024,
            user_id=test_user.id
        )
        
        assert photo.id is not None
        assert photo.filename == "test.jpg"
        assert photo.size == 1024
        assert photo.storage_status == "pending"

    async def test_get_with_metadata(self, async_session: AsyncSession, sample_photo_with_metadata):
        dao = PhotoDAO(async_session)
        photo = await dao.get_with_metadata(sample_photo_with_metadata.id)
        
        assert photo is not None
        assert photo.photo_metadata is not None
        assert photo.photo_metadata.photo_id == photo.id

    async def test_search(self, async_session: AsyncSession, test_user, sample_photos_with_tags):
        dao = PhotoDAO(async_session)
        
        # 测试标签搜索
        photos = await dao.search(
            user_id=test_user.id,
            tags=["nature"],
            limit=10
        )
        assert len(photos) > 0
        # Load tags explicitly before checking
        for photo in photos:
            await async_session.refresh(photo, ["tags"])
        assert all("nature" in [t.name for t in p.tags] for p in photos)
        
        # 测试日期范围搜索
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        photos = await dao.search(
            user_id=test_user.id,
            date_range=(yesterday, tomorrow),
            limit=10
        )
        assert len(photos) > 0
        
        # 测试文件名搜索
        photos = await dao.search(
            user_id=test_user.id,
            filename="sample_0",
            limit=10
        )
        assert len(photos) == 1
        assert photos[0].filename == "sample_0.jpg"

    async def test_get_photos_by_tag(self, async_session: AsyncSession, test_user, sample_photos_with_tags):
        dao = PhotoDAO(async_session)
        
        # 获取带有"nature"标签的照片
        photos = await dao.get_by_tag("nature", test_user.id)
        assert len(photos) > 0
        assert all("nature" in [t.name for t in p.tags] for p in photos)
        
        # 获取带有"city"标签的照片
        photos = await dao.get_by_tag("city", test_user.id)
        assert len(photos) > 0
        assert all("city" in [t.name for t in p.tags] for p in photos)

    async def test_get_storage_stats(self, async_session: AsyncSession, test_user, sample_photos):
        dao = PhotoDAO(async_session)
        stats = await dao.get_storage_stats(user_id=test_user.id)
        
        assert stats["total_photos"] > 0
        assert stats["total_size"] > 0
        assert stats["avg_size"] > 0

    async def test_get_backup_candidates(self, async_session: AsyncSession, test_user, sample_photos):
        dao = PhotoDAO(async_session)
        photos = await dao.get_backup_candidates(user_id=test_user.id, limit=5)
        
        assert len(photos) > 0
        assert all(p.backup_status == "pending" for p in photos)
        assert all(p.storage_status == "completed" for p in photos)

    async def test_update_storage_status(self, async_session: AsyncSession, sample_photo):
        dao = PhotoDAO(async_session)
        success = await dao.update_storage_status(
            photo_id=sample_photo.id,
            status="completed"
        )
        
        assert success
        updated_photo = await dao.get(sample_photo.id)
        assert updated_photo.storage_status == "completed"

@pytest.fixture
async def sample_photo(async_session: AsyncSession) -> Photo:
    dao = PhotoDAO(async_session)
    return await dao.create(
        filename="test.jpg",
        filepath="/test/test.jpg",
        size=1024,
        user_id=1
    )

@pytest.fixture
async def sample_photos(async_session: AsyncSession) -> list[Photo]:
    dao = PhotoDAO(async_session)
    photos = []
    for i in range(5):
        photo = await dao.create(
            filename=f"sample_{i}.jpg",
            filepath=f"/test/sample_{i}.jpg",
            size=1024 * (i + 1),
            user_id=1
        )
        await async_session.refresh(photo)
        # 根据i的奇偶性设置不同的storage_status
        photo.storage_status = "completed" if i % 2 == 0 else "pending"
        await async_session.flush()
        photos.append(photo)
    
    await async_session.commit()
    return photos

@pytest.fixture
async def sample_photos_with_tags(async_session: AsyncSession) -> list[Photo]:
    dao = PhotoDAO(async_session)
    photos = []
    
    # Create tags first
    tags = [
        Tag(name="nature"),
        Tag(name="city"),
        Tag(name="people")
    ]
    async_session.add_all(tags)
    await async_session.flush()
    await async_session.refresh(tags[0])
    await async_session.refresh(tags[1])
    await async_session.refresh(tags[2])

    # Create photos and assign tags
    for i in range(5):
        photo = await dao.create(
            filename=f"sample_{i}.jpg",
            filepath=f"/test/sample_{i}.jpg",
            size=1024 * (i + 1),
            user_id=1
        )
        await async_session.refresh(photo)
        
        # Assign tags based on index
        selected_tags = tags[:2] if i % 2 == 0 else tags[1:]
        for tag in selected_tags:
            # Insert directly into the association table
            await async_session.execute(
                photo_tags.insert().values(
                    photo_id=photo.id,
                    tag_id=tag.id,
                    added_at=datetime.now(timezone.utc)
                )
            )
        photos.append(photo)
    
    await async_session.commit()
    # Explicitly load tags for all photos
    for photo in photos:
        await async_session.refresh(photo, ["tags"])
    return photos
