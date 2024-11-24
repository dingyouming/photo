from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from photo_app.core.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 存储配额相关
    storage_quota: Mapped[int] = mapped_column(Integer, default=10_000_000)  # 默认10MB
    storage_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # 加密相关
    encryption_key: Mapped[Optional[str]] = mapped_column(String(255))
    encryption_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 备份相关
    backup_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_backup_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    backup_frequency: Mapped[int] = mapped_column(Integer, default=7)  # 默认7天
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    albums = relationship("Album", back_populates="user", cascade="all, delete-orphan")

    def update_storage_used(self, size_delta: int) -> bool:
        """
        更新用户已使用的存储空间
        
        Args:
            size_delta: 存储空间变化量（字节），可以是正数或负数
            
        Returns:
            bool: 如果更新成功返回True，如果会超出配额返回False
        """
        new_storage_used = self.storage_used + size_delta
        if size_delta > 0 and new_storage_used > self.storage_quota:
            return False
        
        self.storage_used = max(0, new_storage_used)  # 确保不会小于0
        return True

    def can_backup(self) -> bool:
        """
        检查是否需要进行备份
        
        Returns:
            bool: 如果需要备份返回True，否则返回False
        """
        if not self.backup_enabled:
            return False
            
        if not self.last_backup_date:
            return True
            
        days_since_last_backup = (datetime.now(timezone.utc) - self.last_backup_date).days
        return days_since_last_backup >= self.backup_frequency
