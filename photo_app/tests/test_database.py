import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.base import init_db


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
    try:
        # 删除所有表
        async with test_engine.begin() as conn:
            await conn.run_sync(lambda ctx: ctx.execute(text("""
                DROP TABLE IF EXISTS alembic_version;
                DROP TABLE IF EXISTS photo_metadata;
                DROP TABLE IF EXISTS photo_tags;
                DROP TABLE IF EXISTS photo_albums;
                DROP TABLE IF EXISTS photo;
                DROP TABLE IF EXISTS tag;
                DROP TABLE IF EXISTS album;
                DROP TABLE IF EXISTS user;
            """)))
        
        # 重新初始化数据库
        await init_db()
        
        # 验证表是否创建
        async with test_engine.connect() as conn:
            # 检查用户表
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user'
            """))
            assert result.scalar() is not None
            
            # 检查照片表
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='photo'
            """))
            assert result.scalar() is not None
            
            # 检查标签表
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tag'
            """))
            assert result.scalar() is not None
            
            # 检查相册表
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='album'
            """))
            assert result.scalar() is not None
            
            # 检查元数据表
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='photo_metadata'
            """))
            assert result.scalar() is not None
            
    except SQLAlchemyError as e:
        pytest.fail(f"数据库初始化失败: {str(e)}")

@pytest.mark.asyncio
async def test_database_session(test_session):
    """测试数据库会话管理"""
    try:
        # 测试事务回滚
        async with test_session.begin():
            await test_session.execute(
                text("INSERT INTO user (email, username, hashed_password) VALUES (:email, :username, :password)"),
                {
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "hashedpass"
                }
            )
            # 强制回滚
            raise Exception("测试回滚")
    except Exception:
        pass
    
    # 验证数据已回滚
    result = await test_session.execute(
        text("SELECT COUNT(*) FROM user WHERE email = :email"),
        {"email": "test@example.com"}
    )
    count = result.scalar()
    assert count == 0
    
    # 测试成功提交
    async with test_session.begin():
        await test_session.execute(
            text("INSERT INTO user (email, username, hashed_password) VALUES (:email, :username, :password)"),
            {
                "email": "test2@example.com",
                "username": "testuser2",
                "password": "hashedpass"
            }
        )
    
    # 验证数据已提交
    result = await test_session.execute(
        text("SELECT COUNT(*) FROM user WHERE email = :email"),
        {"email": "test2@example.com"}
    )
    count = result.scalar()
    assert count == 1
