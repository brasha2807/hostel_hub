from sqlalchemy import Column, Integer, String
from database.database import Base


class AdminProfile(Base):
    __tablename__ = "admin_profile"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, default="Arpita Behera")
    title = Column(String, nullable=False, default="Hostel Administrator & Chief Warden")
    email = Column(String, nullable=False, default="arpita.behera@hostelhub.edu")
    phone = Column(String, nullable=False, default="+91 98765 43210")
    office = Column(String, nullable=False, default="Warden Office, Block A")
    photo = Column(String, nullable=True, default="static/banners/warden_profile.jpg")
    status = Column(String, nullable=False, default="Office Online")
