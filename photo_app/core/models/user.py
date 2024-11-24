from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from core.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 用户信息
    full_name = Column(String(100))
    avatar_url = Column(String(1024))
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # 存储配置
    storage_quota = Column(Integer, default=10_000_000_000)  # 10GB
    storage_used = Column(Integer, default=0)
    
    # 偏好设置
    preferences = Column(String(4000))  # JSON格式的用户偏好
    
    # 关系
    photos = relationship("Photo", back_populates="user")
    albums = relationship("Album", back_populates="user")
    
    def update_storage_used(self, size_delta: int) -> bool:
        """
        更新已使用的存储空间
        
        Args:
            size_delta: 存储空间变化量（字节），可以是正数或负数
            
        Returns:
            bool: 是否更新成功（是否超出配额）
        """
        new_storage_used = self.storage_used + size_delta
        if new_storage_used > self.storage_quota:
            return False
        
        if new_storage_used < 0:
            new_storage_used = 0
            
        self.storage_used = new_storage_used
        return True
