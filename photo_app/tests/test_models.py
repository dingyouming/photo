import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.models.photo import Album, Photo, PhotoMetadata, Tag
from core.models.user import User


@pytest.mark.asyncio
async def test_user_crud(test_session):
    """测试用户CRUD操作"""
    # 创建用户
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpass",
        full_name="Test User"
    )
    test_session.add(user)
    await test_session.commit()
    
    # 读取用户
    stmt = select(User).where(User.email == "test@example.com")
    result = await test_session.execute(stmt)
    db_user = result.scalar_one()
    
    assert db_user.username == "testuser"
    assert db_user.full_name == "Test User"
    
    # 更新用户
    db_user.full_name = "Updated Name"
    await test_session.commit()
    
    # 验证更新
    stmt = select(User).where(User.id == db_user.id)
    result = await test_session.execute(stmt)
    updated_user = result.scalar_one()
    assert updated_user.full_name == "Updated Name"
    
    # 删除用户
    await test_session.delete(db_user)
    await test_session.commit()
    
    # 验证删除
    stmt = select(User).where(User.id == db_user.id)
    result = await test_session.execute(stmt)
    assert result.first() is None

@pytest.mark.asyncio
async def test_user_unique_constraints(test_session):
    """测试用户唯一性约束"""
    # 创建第一个用户
    user1 = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpass"
    )
    test_session.add(user1)
    await test_session.commit()
    
    # 尝试创建具有相同email的用户
    user2 = User(
        email="test@example.com",
        username="testuser2",
        hashed_password="hashedpass"
    )
    test_session.add(user2)
    
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()

@pytest.mark.asyncio
async def test_user_storage_quota(test_session):
    """测试用户存储配额管理"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpass",
        storage_quota=1000
    )
    test_session.add(user)
    await test_session.commit()
    
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
async def test_photo_relationships(test_session):
    """测试照片关系"""
    # 创建用户
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpass"
    )
    test_session.add(user)
    await test_session.commit()
    
    # 创建照片
    photo = Photo(
        filename="test.jpg",
        filepath="/path/to/test.jpg",
        size=1000,
        user_id=user.id
    )
    test_session.add(photo)
    await test_session.commit()
    
    # 创建标签
    tag = Tag(name="test_tag", source="manual")
    test_session.add(tag)
    await test_session.commit()
    
    # 创建相册
    album = Album(
        name="Test Album",
        user_id=user.id
    )
    test_session.add(album)
    await test_session.commit()
    
    # 添加关系
    photo.tags.append(tag)
    photo.albums.append(album)
    await test_session.commit()
    
    # 验证关系
    stmt = select(Photo).where(Photo.id == photo.id)
    result = await test_session.execute(stmt)
    db_photo = result.scalar_one()
    
    assert len(db_photo.tags) == 1
    assert db_photo.tags[0].name == "test_tag"
    assert len(db_photo.albums) == 1
    assert db_photo.albums[0].name == "Test Album"

@pytest.mark.asyncio
async def test_photo_metadata(test_session):
    """测试照片元数据"""
    # 创建用户
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpass"
    )
    test_session.add(user)
    await test_session.commit()
    
    # 创建照片
    photo = Photo(
        filename="test.jpg",
        filepath="/path/to/test.jpg",
        size=1000,
        user_id=user.id
    )
    test_session.add(photo)
    await test_session.commit()
    
    # 创建元数据
    metadata = PhotoMetadata(
        photo_id=photo.id,
        color_profile="sRGB",
        dominant_colors='["#FF0000", "#00FF00"]',
        faces_detected=2,
        face_locations='[[10, 20, 30, 40], [50, 60, 70, 80]]',
        scene_type="landscape",
        scene_confidence=0.95
    )
    test_session.add(metadata)
    await test_session.commit()
    
    # 验证关系
    stmt = select(Photo).where(Photo.id == photo.id)
    result = await test_session.execute(stmt)
    db_photo = result.scalar_one()
    
    assert db_photo.metadata is not None
    assert db_photo.metadata.scene_type == "landscape"
    assert db_photo.metadata.faces_detected == 2
