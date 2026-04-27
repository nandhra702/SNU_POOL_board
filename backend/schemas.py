from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserDetails(BaseModel):
    name: str
    phone: str
    year: str
    department: str

class PoolCreate(BaseModel):
    source: str
    destination: str
    departure_time: datetime
    luggage: Optional[str]
    open_to_pool: bool = True
    user: UserDetails

class PoolJoin(BaseModel):
    user: UserDetails

class PoolMemberResponse(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    year: Optional[str]
    department: Optional[str]

    class Config:
        from_attributes = True

class PoolListResponse(BaseModel):
    id: int
    source: str
    destination: str
    departure_time: datetime
    luggage: Optional[str]
    open_to_pool: bool
    people_count: int
    creator_name: Optional[str]
    creator_phone: Optional[str]
    participants: Optional[List[PoolMemberResponse]] = []

    class Config:
        from_attributes = True

class PoolDetailResponse(PoolListResponse):
    pass
