"""数据库测试模块

本模块包含了对数据库基础功能的测试，包括：
1. 数据库连接测试
2. 数据库初始化测试
3. 数据库会话管理测试

注意事项：
- 数据库初始化由test_engine fixture处理，包括表的创建和删除
- 使用异步SQLite数据库进行测试
- 所有测试都使用独立的测试数据库实例
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from dateutil import tz

from photo_app.infrastructure.database.base import init_db


@pytest.mark.asyncio
async def test_database_connection(test_engine):
    """测试数据库连接"""
    try:
        async with test_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            assert row == 1
    except SQLAlchemyError as e:
        pytest.fail(f"数据库连接失败: {str(e)}")

@pytest.mark.asyncio
async def test_database_initialization(test_engine):
    """测试数据库初始化"""
    # 验证表是否创建
    async with test_engine.begin() as conn:
        # 检查用户表
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users'
        """))
        assert result.scalar() is not None

        # 检查照片表
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='photos'
        """))
        assert result.scalar() is not None

        # 检查标签表
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='tags'
        """))
        assert result.scalar() is not None

        # 检查相册表
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='albums'
        """))
        assert result.scalar() is not None

        # 检查元数据表
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='photo_metadata'
        """))
        assert result.scalar() is not None

@pytest.mark.asyncio
async def test_database_session(test_session):
    """测试数据库会话管理"""
    try:
        # 测试事务回滚
        async with test_session.begin():
            await test_session.execute(
                text("""
                    INSERT INTO users (
                        email, username, hashed_password, 
                        is_active, is_superuser,
                        storage_quota, storage_used,
                        encryption_enabled, backup_enabled,
                        backup_frequency,
                        created_at, updated_at
                    ) VALUES (
                        :email, :username, :password,
                        :is_active, :is_superuser,
                        :storage_quota, :storage_used,
                        :encryption_enabled, :backup_enabled,
                        :backup_frequency,
                        :created_at, :updated_at
                    )
                """),
                {
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "hashedpass",
                    "is_active": True,
                    "is_superuser": False,
                    "storage_quota": 1000000,
                    "storage_used": 0,
                    "encryption_enabled": False,
                    "backup_enabled": False,
                    "backup_frequency": 7,
                    "created_at": datetime.now(tz.tzutc()),
                    "updated_at": datetime.now(tz.tzutc())
                }
            )
            # 强制回滚
            raise Exception("测试回滚")
    except Exception:
        pass

    # 验证数据已回滚
    result = await test_session.execute(
        text("SELECT COUNT(*) FROM users WHERE email = :email"),
        {"email": "test@example.com"}
    )
    count = result.scalar()
    assert count == 0

    # 测试成功提交
    await test_session.rollback()  # 确保没有活跃的事务
    async with test_session.begin():
        await test_session.execute(
            text("""
                INSERT INTO users (
                    email, username, hashed_password, 
                    is_active, is_superuser,
                    storage_quota, storage_used,
                    encryption_enabled, backup_enabled,
                    backup_frequency,
                    created_at, updated_at
                ) VALUES (
                    :email, :username, :password,
                    :is_active, :is_superuser,
                    :storage_quota, :storage_used,
                    :encryption_enabled, :backup_enabled,
                    :backup_frequency,
                    :created_at, :updated_at
                )
            """),
            {
                "email": "test2@example.com",
                "username": "testuser2",
                "password": "hashedpass",
                "is_active": True,
                "is_superuser": False,
                "storage_quota": 1000000,
                "storage_used": 0,
                "encryption_enabled": False,
                "backup_enabled": False,
                "backup_frequency": 7,
                "created_at": datetime.now(tz.tzutc()),
                "updated_at": datetime.now(tz.tzutc())
            }
        )

    # 验证提交成功
    result = await test_session.execute(
        text("SELECT COUNT(*) FROM users WHERE email = :email"),
        {"email": "test2@example.com"}
    )
    count = result.scalar()
    assert count == 1
