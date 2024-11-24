from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from photo_app.core.models.base import Base

# 相册和照片的多对多关系表
photo_albums = Table(
    "photo_albums",
    Base.metadata,
    Column("photo_id", ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
    Column("album_id", ForeignKey("albums.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime, default=datetime.utcnow)
)

class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    cover_photo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("photos.id", ondelete="SET NULL"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="albums")
    photos = relationship("Photo", secondary=photo_albums, back_populates="albums")
    cover_photo = relationship("Photo", foreign_keys=[cover_photo_id])
