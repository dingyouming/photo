"""测试配置模块

本模块提供了测试所需的各种fixture，包括：
1. 数据库相关fixture
   - test_engine: 测试数据库引擎
   - test_session: 测试数据库会话
   - db_session: 数据库会话（用于DAO测试）
   - async_session: db_session的别名

2. 测试数据fixture
   - test_user: 测试用户
   - sample_photo: 示例照片
   - sample_photo_with_metadata: 带元数据的示例照片
   - sample_metadata: 示例元数据
   - sample_metadata_list: 示例元数据列表

配置说明：
- 使用SQLite文件数据库进行测试 (./data/test.db)
- 每个测试函数都会获得新的数据库会话
- 自动处理数据库表的创建和清理

注意事项：
- test_engine fixture会自动创建所需的数据库表
- 测试完成后会自动清理数据
- 所有数据库操作都是异步的
"""

import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from photo_app.core.models.base import Base
from photo_app.core.models.user import User
from photo_app.core.models.photo import Photo, PhotoMetadata
from photo_app.core.models.album import Album
from photo_app.core.models.tag import Tag

# 使用临时文件数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///./data/test.db"

@pytest.fixture(scope="function")
async def test_engine():
    """创建测试引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    """创建测试会话"""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False
    )
    
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest.fixture(scope="function")
async def db_session(test_engine):
    """创建数据库会话"""
    # 使用 async_sessionmaker 而不是普通的 sessionmaker
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False
    )
    
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest.fixture(scope="function")
async def async_session(db_session):
    """Alias for db_session to match the parameter name used in tests"""
    yield db_session

@pytest.fixture
async def test_user(test_session: AsyncSession):
    """创建测试用户"""
    from photo_app.core.models.user import User
    
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        storage_quota=1000000,
        storage_used=0
    )
    test_session.add(user)
    await test_session.commit()
    return user

@pytest.fixture
async def sample_photo(test_session: AsyncSession, test_user):
    """Create a sample photo for testing"""
    from photo_app.core.dao.photo import PhotoDAO
    
    dao = PhotoDAO(test_session)
    photo = await dao.create(
        filename="sample.jpg",
        filepath="/test/sample.jpg",
        size=1024,
        user_id=test_user.id
    )
    await test_session.commit()
    return photo

@pytest.fixture
async def sample_photo_with_metadata(test_session: AsyncSession, test_user):
    """Create a sample photo with metadata for testing"""
    from photo_app.core.dao.photo import PhotoDAO
    from photo_app.core.dao.metadata import PhotoMetadataDAO
    
    # Create photo
    photo_dao = PhotoDAO(test_session)
    photo = await photo_dao.create(
        filename="test_with_metadata.jpg",
        filepath="/test/test_with_metadata.jpg",
        size=2048,
        user_id=test_user.id
    )
    
    # Create metadata
    metadata_dao = PhotoMetadataDAO(test_session)
    await metadata_dao.create(
        photo_id=photo.id,
        scene_type="landscape",
        scene_confidence=0.95,
        faces_detected=0,
        aesthetic_score=8.0
    )
    
    await test_session.commit()
    return photo

@pytest.fixture
async def sample_metadata(test_session: AsyncSession, sample_photo):
    """创建测试用的照片元数据"""
    from photo_app.core.dao.metadata import PhotoMetadataDAO
    
    dao = PhotoMetadataDAO(test_session)
    metadata = await dao.create(
        photo_id=sample_photo.id,
        scene_type="landscape",
        scene_confidence=0.95,
        faces_detected=0,
        aesthetic_score=7.5
    )
    await test_session.commit()
    return metadata

@pytest.fixture
async def sample_metadata_list(test_session: AsyncSession, test_user):
    """创建一组测试用的照片元数据"""
    from photo_app.core.dao.photo import PhotoDAO
    from photo_app.core.dao.metadata import PhotoMetadataDAO
    
    photo_dao = PhotoDAO(test_session)
    metadata_dao = PhotoMetadataDAO(test_session)
    metadata_list = []
    
    scene_types = ["landscape", "portrait", "urban", "nature"]
    for i in range(10):
        # 创建照片
        photo = await photo_dao.create(
            filename=f"sample_{i}.jpg",
            filepath=f"/test/sample_{i}.jpg",
            size=1024 * (i + 1),
            user_id=test_user.id
        )
        
        # 创建元数据
        metadata = await metadata_dao.create(
            photo_id=photo.id,
            scene_type=scene_types[i % len(scene_types)],
            scene_confidence=0.8 + (i * 0.02),
            faces_detected=i % 3,
            aesthetic_score=5.0 + (i * 0.5)
        )
        metadata_list.append(metadata)
    
    await test_session.commit()
    return metadata_list
