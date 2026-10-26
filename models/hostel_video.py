from sqlalchemy import Column, Integer, String
from database.database import Base


class HostelVideo(Base):
    __tablename__ = "hostel_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    video_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    room_capacity = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
