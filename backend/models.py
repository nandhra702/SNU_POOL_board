from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users_v2"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    year = Column(String, nullable=False)
    department = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pools_created = relationship("Pool", back_populates="creator")
    pools_joined = relationship("PoolMember", back_populates="user")

class Pool(Base):
    __tablename__ = "pools_v2"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users_v2.id", ondelete="CASCADE"))
    source = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    luggage = Column(String, nullable=True)
    open_to_pool = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="pools_created")
    members = relationship("PoolMember", back_populates="pool")

    __table_args__ = (
        Index('idx_pools_search_v2', "source", "destination", "departure_time"),
    )

class PoolMember(Base):
    __tablename__ = "pool_members_v2"

    pool_id = Column(Integer, ForeignKey("pools_v2.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users_v2.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    pool = relationship("Pool", back_populates="members")
    user = relationship("User", back_populates="pools_joined")
