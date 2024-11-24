from typing import List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from core.models.base import Base

# Many-to-many relationship tables
photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photo.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)

photo_albums = Table(
    "photo_albums",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photo.id"), primary_key=True),
    Column("album_id", Integer, ForeignKey("album.id"), primary_key=True),
)


class Photo(Base):
    __tablename__ = "photo"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1024), nullable=False, unique=True)
    thumbnail_path = Column(String(1024))
    
    # 基本信息
    size = Column(Integer, nullable=False)  # 文件大小（字节）
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(20))  # 图片格式 (JPEG, PNG等)
    
    # EXIF数据
    camera_make = Column(String(100))
    camera_model = Column(String(100))
    focal_length = Column(Float)
    exposure_time = Column(String(50))
    aperture = Column(Float)
    iso = Column(Integer)
    taken_at = Column(DateTime)
    
    # 地理信息
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    location_name = Column(String(255))
    
    # AI生成的描述
    description = Column(String(1000))
    
    # 关系
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="photos")
    
    tags = relationship("Tag", secondary=photo_tags, back_populates="photos")
    albums = relationship("Album", secondary=photo_albums, back_populates="photos")
    
    # 元数据
    metadata = relationship("PhotoMetadata", back_populates="photo", uselist=False)


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    source = Column(String(20))  # manual, ai, exif
    confidence = Column(Float)  # AI标签的置信度
    
    photos = relationship("Photo", secondary=photo_tags, back_populates="tags")


class Album(Base):
    __tablename__ = "album"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    cover_photo_id = Column(Integer, ForeignKey("photo.id"))
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    photos = relationship("Photo", secondary=photo_albums, back_populates="albums")
    user = relationship("User", back_populates="albums")


class PhotoMetadata(Base):
    __tablename__ = "photo_metadata"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photo.id"), unique=True, nullable=False)
    
    # 颜色信息
    color_profile = Column(String(50))
    dominant_colors = Column(String(255))  # JSON格式的颜色列表
    
    # 人脸检测
    faces_detected = Column(Integer)
    face_locations = Column(String(1000))  # JSON格式的人脸位置
    
    # 场景分类
    scene_type = Column(String(100))
    scene_confidence = Column(Float)
    
    # 图像质量
    blur_score = Column(Float)
    exposure_score = Column(Float)
    aesthetic_score = Column(Float)
    
    # 其他元数据
    raw_exif = Column(String(4000))  # JSON格式的原始EXIF数据
    
    photo = relationship("Photo", back_populates="metadata")
