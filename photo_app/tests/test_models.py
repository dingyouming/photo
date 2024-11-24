import pytest
from datetime import datetime, timezone
from sqlalchemy import select, insert, delete, Table, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from photo_app.core.models.photo import Photo, PhotoMetadata
from photo_app.core.models.album import Album, photo_albums
from photo_app.core.models.tag import Tag, photo_tags
from photo_app.core.models.user import User

@pytest.mark.asyncio
async def test_user_crud(db_session):
    """测试用户CRUD操作"""
    # 创建用户
    user = User(
        email="test1@example.com",
        username="testuser1",
        hashed_password="hashedpass",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 读取用户
    stmt = select(User).where(User.email == "test1@example.com")
    result = await db_session.execute(stmt)
    db_user = result.scalar_one()
    
    assert db_user.username == "testuser1"
    assert db_user.full_name == "Test User"
    assert db_user.is_active is True
    assert db_user.storage_quota == 10000000
    assert db_user.storage_used == 0
    
    # 更新用户
    db_user.full_name = "Updated Name"
    await db_session.commit()
    await db_session.refresh(db_user)
    
    # 验证更新
    stmt = select(User).where(User.id == db_user.id)
    result = await db_session.execute(stmt)
    updated_user = result.scalar_one()
    assert updated_user.full_name == "Updated Name"
    
    # 删除用户
    await db_session.delete(db_user)
    await db_session.commit()
    
    # 验证删除
    stmt = select(User).where(User.id == db_user.id)
    result = await db_session.execute(stmt)
    assert result.first() is None

@pytest.mark.asyncio
async def test_user_unique_constraints(db_session):
    """测试用户唯一性约束"""
    # 创建第一个用户
    user1 = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password="hashedpass",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user1)
    await db_session.commit()
    await db_session.refresh(user1)
    
    # 尝试创建具有相同email的用户
    user2 = User(
        email="test2@example.com",  # 相同的邮箱
        username="testuser2_duplicate",
        hashed_password="hashedpass",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user2)
    
    # 验证唯一性约束
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # 尝试创建具有相同用户名的用户
    user3 = User(
        email="test3@example.com",
        username="testuser2",  # 相同的用户名
        hashed_password="hashedpass",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user3)
    
    # 验证唯一性约束
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

@pytest.mark.asyncio
async def test_user_storage_quota(db_session):
    """测试用户存储配额管理"""
    user = User(
        email="test3@example.com",
        username="testuser3",
        hashed_password="hashedpass",
        storage_quota=1000
    )
    db_session.add(user)
    await db_session.commit()
    
    # 测试正常增加存储
    assert user.update_storage_used(500) is True
    assert user.storage_used == 500
    
    # 测试超出配额
    assert user.update_storage_used(600) is False
    assert user.storage_used == 500
    
    # 测试减少存储
    assert user.update_storage_used(-200) is True
    assert user.storage_used == 300

@pytest.mark.asyncio
async def test_photo_relationships(db_session):
    """测试照片关系"""
    # 创建用户
    user = User(
        email="test4@example.com",
        username="testuser4",
        hashed_password="hashedpass"
    )
    db_session.add(user)
    await db_session.commit()
    
    # 创建照片
    photo = Photo(
        filename="test_rel.jpg",
        filepath="/path/to/test_rel.jpg",
        size=1000,
        user_id=user.id
    )
    db_session.add(photo)
    await db_session.commit()
    
    # 创建标签
    tag = Tag(name="test_tag", description="Test tag for photo relationships", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    db_session.add(tag)
    await db_session.commit()
    
    # 创建相册
    album = Album(
        name="Test Album",
        user_id=user.id
    )
    db_session.add(album)
    await db_session.commit()
    
    # 添加关系
    await db_session.execute(
        insert(photo_tags).values(photo_id=photo.id, tag_id=tag.id)
    )
    await db_session.execute(
        insert(photo_albums).values(photo_id=photo.id, album_id=album.id)
    )
    await db_session.commit()
    
    # 验证关系
    stmt = select(Photo).options(selectinload(Photo.tags), selectinload(Photo.albums)).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    db_photo = result.scalar_one()
    
    assert len(db_photo.tags) == 1
    assert db_photo.tags[0].name == "test_tag"
    assert len(db_photo.albums) == 1
    assert db_photo.albums[0].name == "Test Album"

@pytest.mark.asyncio
async def test_photo_metadata(db_session):
    """测试照片元数据"""
    # 创建用户
    user = User(
        email="test5@example.com",
        username="test_user5",
        hashed_password="hashedpass"
    )
    db_session.add(user)
    await db_session.commit()

    # 创建照片
    photo = Photo(
        filename="test_meta.jpg",
        filepath="/path/to/test_meta.jpg",
        size=1024,
        user_id=user.id,
    )
    db_session.add(photo)
    await db_session.commit()

    # 创建照片元数据
    photo_metadata = PhotoMetadata(
        photo_id=photo.id,
        color_profile="sRGB",
        dominant_colors="red,blue",
        faces_detected=2,
        face_locations="[[10,20,30,40],[50,60,70,80]]",
        scene_type="landscape",
        scene_confidence=0.95,
        blur_score=0.1,
        exposure_score=0.8,
        aesthetic_score=0.9,
        raw_exif='{"make":"Canon","model":"EOS R5"}',
    )
    db_session.add(photo_metadata)
    await db_session.commit()

    # 验证关系
    stmt = select(Photo).options(selectinload(Photo.photo_metadata)).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    loaded_photo = result.scalar_one()
    
    assert loaded_photo.photo_metadata.color_profile == "sRGB"
    assert loaded_photo.photo_metadata.dominant_colors == "red,blue"
    assert loaded_photo.photo_metadata.faces_detected == 2
    assert loaded_photo.photo_metadata.scene_type == "landscape"
    assert loaded_photo.photo_metadata.scene_confidence == 0.95
    assert loaded_photo.photo_metadata.blur_score == 0.1
    assert loaded_photo.photo_metadata.exposure_score == 0.8
    assert loaded_photo.photo_metadata.aesthetic_score == 0.9
    assert loaded_photo.photo_metadata.photo.id == photo.id

@pytest.mark.asyncio
async def test_album_operations(db_session):
    """测试相册操作"""
    # 创建用户
    user = User(
        email="test6@example.com",
        username="testuser6",
        hashed_password="hashedpass",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 创建相册
    album = Album(
        name="Vacation 2024",
        description="My vacation photos",
        user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(album)
    await db_session.commit()
    await db_session.refresh(album)

    # 创建多张照片
    photos = []
    for i in range(3):
        photo = Photo(
            filename=f"vacation_{i}.jpg",
            filepath=f"/path/to/vacation_{i}.jpg",
            size=1000,
            user_id=user.id,
            storage_status="pending",
            backup_status="pending",
            is_encrypted=False,
            version=1,
            version_date=datetime.now(timezone.utc),
            retry_count=0,
            upload_date=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        photos.append(photo)
        db_session.add(photo)
    await db_session.commit()
    
    # 刷新照片对象以获取ID
    for photo in photos:
        await db_session.refresh(photo)

    # 添加照片到相册
    for photo in photos:
        await db_session.execute(
            insert(photo_albums).values(
                photo_id=photo.id,
                album_id=album.id
            )
        )
    await db_session.commit()

    # 验证相册中的照片数量
    stmt = select(func.count()).select_from(photo_albums).where(photo_albums.c.album_id == album.id)
    result = await db_session.execute(stmt)
    count = result.scalar()
    assert count == 3

    # 测试从相册中移除照片
    await db_session.execute(
        delete(photo_albums).where(
            photo_albums.c.album_id == album.id,
            photo_albums.c.photo_id == photos[0].id
        )
    )
    await db_session.commit()

    # 验证照片被移除
    stmt = select(func.count()).select_from(photo_albums).where(photo_albums.c.album_id == album.id)
    result = await db_session.execute(stmt)
    count = result.scalar()
    assert count == 2

@pytest.mark.asyncio
async def test_tag_operations(db_session):
    """测试标签操作"""
    # 创建用户
    user = User(
        email="test7@example.com",
        username="testuser7",
        hashed_password="hashedpass",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 创建照片
    photo = Photo(
        filename="tag_test.jpg",
        filepath="/path/to/tag_test.jpg",
        size=1000,
        user_id=user.id,
        storage_status="pending",
        backup_status="pending",
        is_encrypted=False,
        version=1,
        version_date=datetime.now(timezone.utc),
        retry_count=0,
        upload_date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(photo)
    await db_session.commit()
    await db_session.refresh(photo)

    # 创建并添加多个标签
    tags = []
    tag_names = ["nature", "landscape", "sunset"]
    for tag_name in tag_names:
        tag = Tag(
            name=tag_name,
            description=f"Description for {tag_name} tag",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        tags.append(tag)
        db_session.add(tag)
    await db_session.commit()
    
    # 将标签添加到照片
    for tag in tags:
        await db_session.execute(
            insert(photo_tags).values(
                photo_id=photo.id,
                tag_id=tag.id
            )
        )
    await db_session.commit()
    
    # 验证标签是否正确添加
    stmt = select(Tag).join(Photo.tags).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    photo_tags_result = result.scalars().all()
    
    assert len(photo_tags_result) == 3
    assert all(tag.name in tag_names for tag in photo_tags_result)

    # 测试删除标签
    await db_session.execute(
        delete(photo_tags).where(
            photo_tags.c.photo_id == photo.id,
            photo_tags.c.tag_id == tags[0].id
        )
    )
    await db_session.commit()
    
    # 验证标签是否正确删除
    stmt = select(Tag).join(Photo.tags).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    remaining_tags = result.scalars().all()
    
    assert len(remaining_tags) == 2
    assert tags[0].name not in [tag.name for tag in remaining_tags]

@pytest.mark.asyncio
async def test_cascade_delete(db_session):
    """测试级联删除"""
    # 创建用户
    user = User(
        email="test8@example.com",
        username="testuser8",
        hashed_password="hashedpass",
        is_active=True,
        is_superuser=False,
        storage_quota=10000000,
        storage_used=0,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 创建照片
    photo = Photo(
        filename="cascade_test.jpg",
        filepath="/path/to/cascade_test.jpg",
        size=1000,
        user_id=user.id,
        storage_status="pending",
        backup_status="pending",
        is_encrypted=False,
        version=1,
        version_date=datetime.now(timezone.utc),
        retry_count=0,
        upload_date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(photo)
    await db_session.commit()
    await db_session.refresh(photo)

    # 创建照片元数据
    metadata = PhotoMetadata(
        photo_id=photo.id,
        color_profile="sRGB",
        dominant_colors="blue,green",
        faces_detected=2,
        face_locations="[[100,100,200,200],[300,300,400,400]]",
        scene_type="landscape",
        scene_confidence=85,
        blur_score=20,
        exposure_score=90,
        aesthetic_score=85,
        raw_exif="{}",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(metadata)
    await db_session.commit()
    await db_session.refresh(metadata)

    # 创建标签
    tag = Tag(
        name="test_tag",
        description="Test tag for cascade delete",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    # 添加标签到照片
    stmt = insert(photo_tags).values(photo_id=photo.id, tag_id=tag.id)
    await db_session.execute(stmt)
    await db_session.commit()

    # 删除照片
    await db_session.delete(photo)
    await db_session.commit()

    # 验证照片元数据是否被删除
    stmt = select(PhotoMetadata).where(PhotoMetadata.photo_id == photo.id)
    result = await db_session.execute(stmt)
    assert result.first() is None

    # 验证标签关联是否被删除，但标签本身仍然存在
    stmt = select(Tag).where(Tag.id == tag.id)
    result = await db_session.execute(stmt)
    assert result.scalar_one() == tag

@pytest.mark.asyncio
async def test_user_storage_limit(db_session):
    """测试用户存储限制"""
    # 创建用户，设置较小的存储配额
    user = User(
        email="test9@example.com",
        username="testuser9",
        hashed_password="hashedpass",
        storage_quota=2000,  # 2KB配额
        storage_used=0,
        is_active=True,
        is_superuser=False,
        encryption_enabled=False,
        backup_enabled=True,
        backup_frequency=7,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 添加第一张照片（在配额内）
    photo1 = Photo(
        filename="within_quota.jpg",
        filepath="/path/to/within_quota.jpg",
        size=1000,
        user_id=user.id,
        storage_status="pending",
        backup_status="pending",
        is_encrypted=False,
        version=1,
        version_date=datetime.now(timezone.utc),
        retry_count=0,
        upload_date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(photo1)
    await db_session.commit()
    await db_session.refresh(photo1)

    # 更新用户的存储使用量
    user.update_storage_used(photo1.size)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.storage_used == 1000

    # 尝试添加超出配额的照片
    photo2 = Photo(
        filename="exceed_quota.jpg",
        filepath="/path/to/exceed_quota.jpg",
        size=1500,  # 这会超出2KB的配额
        user_id=user.id,
        storage_status="pending",
        backup_status="pending",
        is_encrypted=False,
        version=1,
        version_date=datetime.now(timezone.utc),
        retry_count=0,
        upload_date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(photo2)
    await db_session.commit()
    await db_session.refresh(photo2)
    
    # 验证是否能检测到配额超出
    assert not user.update_storage_used(photo2.size)
    await db_session.rollback()

@pytest.mark.asyncio
async def test_storage_backup_restore(db_session):
    """测试存储备份和恢复功能"""
    # 创建用户
    user = User(
        email="backup_test@example.com",
        username="backup_user",
        hashed_password="hashedpass",
        storage_quota=10000
    )
    db_session.add(user)
    await db_session.commit()

    # 创建原始照片和元数据
    original_photos = []
    for i in range(3):
        photo = Photo(
            filename=f"backup_test_{i}.jpg",
            filepath=f"/path/to/backup/backup_test_{i}.jpg",
            size=1000,
            user_id=user.id,
            backup_status="pending",
            backup_path=None
        )
        original_photos.append(photo)
        db_session.add(photo)
    await db_session.commit()

    # 模拟备份过程
    for photo in original_photos:
        photo.backup_status = "completed"
        photo.backup_path = f"/backup/store/{photo.id}_{photo.filename}"
    await db_session.commit()

    # 验证备份状态
    stmt = select(Photo).where(Photo.user_id == user.id)
    result = await db_session.execute(stmt)
    backed_up_photos = result.scalars().all()
    assert all(photo.backup_status == "completed" for photo in backed_up_photos)
    assert all(photo.backup_path is not None for photo in backed_up_photos)

    # 模拟恢复过程
    for photo in backed_up_photos:
        photo.restore_status = "in_progress"
    await db_session.commit()

    # 验证恢复状态
    for photo in backed_up_photos:
        photo.restore_status = "completed"
    await db_session.commit()

    await db_session.refresh(user)
    stmt = select(Photo).where(Photo.user_id == user.id)
    result = await db_session.execute(stmt)
    restored_photos = result.scalars().all()
    assert all(photo.restore_status == "completed" for photo in restored_photos)

@pytest.mark.asyncio
async def test_storage_encryption(db_session):
    """测试存储加密功能"""
    from datetime import datetime
    
    # 创建用户
    user = User(
        email="security_test@example.com",
        username="security_user",
        hashed_password="hashedpass",
        encryption_key="test_encryption_key"
    )
    db_session.add(user)
    await db_session.commit()

    # 创建加密照片
    photo = Photo(
        filename="encrypted_photo.jpg",
        filepath="/path/to/security/encrypted_photo.jpg",
        size=1000,
        user_id=user.id,
        is_encrypted=True,
        encryption_date=datetime.now(timezone.utc),
        encryption_method="AES-256"
    )
    db_session.add(photo)
    await db_session.commit()

    # 验证加密状态
    stmt = select(Photo).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    encrypted_photo = result.scalar_one()
    assert encrypted_photo.is_encrypted
    assert encrypted_photo.encryption_method == "AES-256"
    assert encrypted_photo.encryption_date is not None

@pytest.mark.asyncio
async def test_storage_versioning(db_session):
    """测试存储版本控制"""
    from datetime import datetime

    # 创建用户
    user = User(
        email="version_test@example.com",
        username="version_user",
        hashed_password="hashedpass"
    )
    db_session.add(user)
    await db_session.commit()

    # 创建原始照片
    photo = Photo(
        filename="version_test.jpg",
        filepath="/path/to/version/version_test.jpg",
        size=1000,
        user_id=user.id,
        version=1,
        version_date=datetime.now(timezone.utc)
    )
    db_session.add(photo)
    await db_session.commit()

    # 创建照片版本历史
    version_dates = []
    for i in range(2, 4):  # 创建两个新版本
        photo.version = i
        photo.version_date = datetime.now(timezone.utc)
        version_dates.append(photo.version_date)
        await db_session.commit()

    # 验证版本历史
    stmt = select(Photo).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    versioned_photo = result.scalar_one()
    assert versioned_photo.version == 3
    assert versioned_photo.version_date > version_dates[0]

@pytest.mark.asyncio
async def test_storage_recovery(db_session):
    """测试存储故障恢复"""
    # 创建用户
    user = User(
        email="recovery_test@example.com",
        username="recovery_user",
        hashed_password="hashedpass"
    )
    db_session.add(user)
    await db_session.commit()

    # 创建照片并模拟存储故障
    photo = Photo(
        filename="recovery_test.jpg",
        filepath="/path/to/recovery/recovery_test.jpg",
        size=1000,
        user_id=user.id,
        storage_status="failed",
        failure_reason="Network timeout",
        retry_count=0
    )
    db_session.add(photo)
    await db_session.commit()

    # 模拟重试过程
    max_retries = 3
    while photo.storage_status == "failed" and photo.retry_count < max_retries:
        photo.retry_count += 1
        if photo.retry_count == max_retries:
            photo.storage_status = "completed"
            photo.failure_reason = None
    await db_session.commit()

    # 验证恢复状态
    stmt = select(Photo).where(Photo.id == photo.id)
    result = await db_session.execute(stmt)
    recovered_photo = result.scalar_one()
    assert recovered_photo.storage_status == "completed"
    assert recovered_photo.failure_reason is None
    assert recovered_photo.retry_count == max_retries
