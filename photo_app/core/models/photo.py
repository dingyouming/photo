from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from photo_app.core.models.base import Base

# 照片-标签关联表和照片-相册关联表已移至各自的模型文件中

class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # 存储状态相关字段
    storage_status: Mapped[str] = mapped_column(String(20), default="pending")
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 备份相关字段
    backup_status: Mapped[str] = mapped_column(String(20), default="pending")
    backup_path: Mapped[Optional[str]] = mapped_column(String(255))
    restore_status: Mapped[Optional[str]] = mapped_column(String(20))
    
    # 加密相关字段
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    encryption_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    encryption_method: Mapped[Optional[str]] = mapped_column(String(50))
    
    # 版本控制字段
    version: Mapped[int] = mapped_column(Integer, default=1)
    version_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    user = relationship("User", back_populates="photos")
    photo_metadata = relationship("PhotoMetadata", back_populates="photo", uselist=False, cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="photo_tags", back_populates="photos")
    albums = relationship("Album", secondary="photo_albums", back_populates="photos")

class PhotoMetadata(Base):
    __tablename__ = "photo_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), unique=True)
    color_profile: Mapped[Optional[str]] = mapped_column(String(50))
    dominant_colors: Mapped[Optional[str]] = mapped_column(String(255))
    faces_detected: Mapped[Optional[int]] = mapped_column(Integer)
    face_locations: Mapped[Optional[str]] = mapped_column(String(1000))
    scene_type: Mapped[Optional[str]] = mapped_column(String(50))
    scene_confidence: Mapped[Optional[float]] = mapped_column(Integer)
    blur_score: Mapped[Optional[float]] = mapped_column(Integer)
    exposure_score: Mapped[Optional[float]] = mapped_column(Integer)
    aesthetic_score: Mapped[Optional[float]] = mapped_column(Integer)
    raw_exif: Mapped[Optional[str]] = mapped_column(String(4000))

    photo = relationship("Photo", back_populates="photo_metadata")
