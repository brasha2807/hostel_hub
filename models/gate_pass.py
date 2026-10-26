from sqlalchemy import Column, Integer, String
from database.database import Base


class GatePass(Base):
    __tablename__ = "gate_passes"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, nullable=False)

    reason = Column(String, nullable=False)

    pass_date = Column(String, nullable=False)

    out_time = Column(String, nullable=False)
    in_time = Column(String, nullable=True)

    status = Column(String, nullable=False, default="Out")