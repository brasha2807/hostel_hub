from sqlalchemy import Column, Integer, String
from database.database import Base


class Student(Base):
    __tablename__ = "students"

    # Basic student information
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    course = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    # Parent / Guardian information
    parent_name = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)

    # Student address
    address = Column(String, nullable=True)

    # Admission information
    admission_date = Column(String, nullable=True)

    # Profile status
    profile_status = Column(
        String,
        nullable=False,
        default="Active"
    )

    # Student Photo / Avatar path or URL
    photo = Column(String, nullable=True)

    # Allocated Room Number
    room_number = Column(String, nullable=True)
