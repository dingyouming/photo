# 照片管理系统数据库实施指南

## 一、数据库选择

### 1.1 开发环境
- 使用 SQLite
  - 优点：轻量级，无需额外服务
  - 适用场景：本地开发和小规模部署
  - 配置简单，可移植性强

### 1.2 生产环境
- 使用 PostgreSQL
  - 优点：稳定可靠，功能丰富
  - 适用场景：生产部署和大规模应用
  - 支持高并发和复杂查询

## 二、数据库设计

### 2.1 核心表结构
```sql
-- 照片基本信息表
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    onedrive_id TEXT,           -- OneDrive 文件ID
    backup_id TEXT,                      -- 备份云盘文件ID（可选）
    sync_status INTEGER DEFAULT 0        -- 同步状态
);

-- 照片元数据表
CREATE TABLE metadata (
    photo_id INTEGER PRIMARY KEY,
    metadata_json TEXT NOT NULL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exif_data JSON,                      -- EXIF 元数据
    ai_tags JSON,                        -- AI 生成的标签
    user_tags TEXT[],                    -- 用户标签
    FOREIGN KEY (photo_id) REFERENCES photos(id)
);

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 照片-标签关联表
CREATE TABLE photo_tags (
    photo_id INTEGER,
    tag_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (photo_id, tag_id),
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 相册表
CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 相册-照片关联表
CREATE TABLE album_photos (
    album_id INTEGER,
    photo_id INTEGER,
    position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (album_id, photo_id),
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE
);

-- 存储配置表
CREATE TABLE storage_config (
    id INTEGER PRIMARY KEY,
    provider TEXT NOT NULL,              -- 'onedrive' 或 'backup'
    credentials JSON,                    -- 加密的认证信息
    sync_settings JSON,                  -- 同步配置
    last_sync TIMESTAMP                  -- 最后同步时间
);

-- 同步日志表
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY,
    photo_id INTEGER,
    operation TEXT,                      -- 'upload', 'download', 'delete'
    status TEXT,                         -- 'success', 'failed'
    timestamp TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (photo_id) REFERENCES photos(id)
);
```

### 2.2 索引设计
```sql
-- 文件路径索引
CREATE INDEX idx_photos_file_path ON photos(file_path);

-- 创建时间索引
CREATE INDEX idx_photos_created_at ON photos(created_at);

-- 标签名称索引
CREATE INDEX idx_tags_name ON tags(name);

-- 相册名称索引
CREATE INDEX idx_albums_name ON albums(name);

-- OneDrive ID 索引
CREATE INDEX idx_onedrive_id ON photos(onedrive_id);

-- 文件路径索引
CREATE INDEX idx_file_path ON photos(path);

-- 同步状态索引
CREATE INDEX idx_sync_status ON photos(sync_status);
```

## 三、SQLAlchemy 最佳实践

### 3.1 基础模型配置
```python
from datetime import datetime, timezone
from sqlalchemy.orm import as_declarative, declared_attr

@as_declarative()
class Base:
    # 自动生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # 使用 timezone-aware 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
```

### 3.2 异步关系加载
在异步上下文中加载关系时，使用 selectinload 而不是 lazy loading：

```python
from sqlalchemy.orm import selectinload

# 正确的做法
stmt = select(Photo).options(
    selectinload(Photo.tags), 
    selectinload(Photo.albums)
).where(Photo.id == photo_id)
result = await session.execute(stmt)
photo = result.scalar_one()

# 避免的做法
photo = await session.get(Photo, photo_id)
await session.refresh(photo)  # 可能导致 N+1 查询问题
```

### 3.3 SQLAlchemy 2.0 兼容性
- 使用 `sqlalchemy.orm` 中的新式导入路径
- 避免使用已弃用的 API（如 `sqlalchemy.ext.declarative`）
- 使用 timezone-aware 的 datetime 对象

### 3.4 数据库初始化和测试
```python
# 数据库初始化
async def init_db(custom_engine=None) -> None:
    """初始化数据库
    
    Args:
        custom_engine: 可选的自定义数据库引擎，主要用于测试
    """
    target_engine = custom_engine or engine
    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 测试配置
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
```

### 3.5 测试最佳实践
1. 使用独立的测试数据库
   - 配置专门的测试数据库 URL
   - 避免污染开发/生产数据库

2. 自动化的表管理
   - 测试前自动创建所需的表
   - 测试后自动清理数据
   - 使用 fixture 管理数据库生命周期

3. 事务管理
   - 每个测试在独立的事务中运行
   - 测试结束后自动回滚
   - 避免测试之间的数据干扰

4. 异步测试支持
   - 使用 pytest-asyncio 运行异步测试
   - 正确处理异步上下文
   - 避免混用同步和异步操作

## 四、数据访问层

### 4.1 基础 DAO 实现
```python
from typing import List, Dict, Any
from datetime import datetime

class PhotoDAO:
    def __init__(self, db_session):
        self.session = db_session

    async def create(self, file_path: str, file_name: str, 
                    file_size: int) -> int:
        """创建新的照片记录"""
        query = """
        INSERT INTO photos (file_path, file_name, file_size)
        VALUES (?, ?, ?)
        RETURNING id
        """
        return await self.session.execute(
            query, (file_path, file_name, file_size)
        )

    async def get_by_id(self, photo_id: int) -> Dict[str, Any]:
        """根据ID获取照片信息"""
        query = """
        SELECT p.*, m.metadata_json
        FROM photos p
        LEFT JOIN metadata m ON p.id = m.photo_id
        WHERE p.id = ?
        """
        return await self.session.fetch_one(query, (photo_id,))

    async def update(self, photo_id: int, 
                    updates: Dict[str, Any]) -> bool:
        """更新照片信息"""
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        query = f"""
        UPDATE photos
        SET {set_clause}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        values = list(updates.values()) + [photo_id]
        return await self.session.execute(query, values)

class StorageManager:
    async def upload_to_onedrive(self, file_path: str) -> str:
        """上传文件到 OneDrive 并返回文件ID"""
        pass

    async def backup_file(self, file_path: str, onedrive_id: str) -> str:
        """备份文件到第二个云盘"""
        pass

    async def verify_file_integrity(self, photo_id: int) -> bool:
        """验证文件完整性（主存储和备份）"""
        pass
```

### 4.2 高级查询实现
```python
class PhotoQueryService:
    def __init__(self, db_session):
        self.session = db_session

    async def search_photos(self, 
                          tags: List[str] = None,
                          date_range: tuple = None,
                          text_search: str = None) -> List[Dict]:
        """复合条件搜索照片"""
        query = """
        SELECT DISTINCT p.*
        FROM photos p
        LEFT JOIN photo_tags pt ON p.id = pt.photo_id
        LEFT JOIN tags t ON pt.tag_id = t.id
        WHERE 1=1
        """
        params = []
        
        if tags:
            placeholders = ','.join(['?' for _ in tags])
            query += f" AND t.name IN ({placeholders})"
            params.extend(tags)
            
        if date_range:
            start_date, end_date = date_range
            query += " AND p.created_at BETWEEN ? AND ?"
            params.extend([start_date, end_date])
            
        if text_search:
            query += """ AND (
                p.file_name LIKE ? OR 
                EXISTS (
                    SELECT 1 FROM metadata m 
                    WHERE m.photo_id = p.id 
                    AND m.metadata_json LIKE ?
                )
            )"""
            search_pattern = f"%{text_search}%"
            params.extend([search_pattern, search_pattern])
            
        return await self.session.fetch_all(query, params)

class SyncManager:
    async def sync_to_onedrive(self) -> None:
        """同步本地更改到 OneDrive"""
        pass

    async def sync_to_backup(self) -> None:
        """同步到备份云盘"""
        pass

    async def verify_sync_status(self) -> Dict[str, Any]:
        """检查同步状态"""
        pass
```

## 五、数据迁移

### 5.1 迁移脚本
```python
# migrations/001_initial.py
from yoyo import step

steps = [
    step("""
        CREATE TABLE photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            onedrive_id TEXT,           -- OneDrive 文件ID
            backup_id TEXT,                      -- 备份云盘文件ID（可选）
            sync_status INTEGER DEFAULT 0        -- 同步状态
        )
    """),
    # ... 其他表的创建语句
]

# migrations/002_add_storage_config.py
from yoyo import step

steps = [
    step("""
        CREATE TABLE storage_config (
            id INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,              -- 'onedrive' 或 'backup'
            credentials JSON,                    -- 加密的认证信息
            sync_settings JSON,                  -- 同步配置
            last_sync TIMESTAMP                  -- 最后同步时间
        )
    """),
    # ... 其他表的创建语句
]

# migrations/003_add_sync_log.py
from yoyo import step

steps = [
    step("""
        CREATE TABLE sync_log (
            id INTEGER PRIMARY KEY,
            photo_id INTEGER,
            operation TEXT,                      -- 'upload', 'download', 'delete'
            status TEXT,                         -- 'success', 'failed'
            timestamp TIMESTAMP,
            error_message TEXT,
            FOREIGN KEY (photo_id) REFERENCES photos(id)
        )
    """),
    # ... 其他表的创建语句
]
```

### 5.2 迁移管理
```python
from yoyo import read_migrations
from yoyo import get_backend

def apply_migrations(db_url: str):
    backend = get_backend(db_url)
    migrations = read_migrations('migrations')
    
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
```

## 六、性能优化

### 6.1 查询优化
- 使用适当的索引
- 优化JOIN操作
- 使用预编译语句
- 实现结果缓存

### 6.2 连接池管理
- 合理设置池大小
- 监控连接使用
- 处理连接泄露

## 七、维护指南

### 7.1 日常维护
- 定期备份数据
- 检查数据一致性
- 优化数据库性能
- 清理临时数据

### 7.2 故障处理
- 数据库备份恢复
- 索引重建
- 数据修复
- 性能诊断

### 7.3 监控指标
- 查询性能分析
- 存储空间使用
- 同步队列状态
- API 响应时间
