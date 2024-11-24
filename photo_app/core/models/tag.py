from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from photo_app.core.models.base import Base

# 标签和照片的多对多关系表
photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime, default=datetime.utcnow)
)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    photos = relationship("Photo", secondary=photo_tags, back_populates="tags")
