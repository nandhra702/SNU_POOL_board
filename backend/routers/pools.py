from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, timezone
import models, schemas, database

router = APIRouter(prefix="/api/pools", tags=["pools"])

def get_or_create_user(db: Session, user_details: schemas.UserDetails):
    user = db.query(models.User).filter(models.User.phone == user_details.phone).first()
    if not user:
        user = models.User(
            phone=user_details.phone,
            name=user_details.name,
            year=user_details.year,
            department=user_details.department
        )
        db.add(user)
    else:
        # Update user details if they changed
        user.name = user_details.name
        user.year = user_details.year
        user.department = user_details.department
    db.commit()
    db.refresh(user)
    return user

@router.post("/", response_model=schemas.PoolListResponse)
def create_pool(
    pool_in: schemas.PoolCreate,
    db: Session = Depends(database.get_db)
):
    user = get_or_create_user(db, pool_in.user)
        
    db_pool = models.Pool(
        creator_id=user.id,
        source=pool_in.source,
        destination=pool_in.destination,
        departure_time=pool_in.departure_time,
        luggage=pool_in.luggage,
        open_to_pool=pool_in.open_to_pool
    )
    db.add(db_pool)
    db.commit()
    db.refresh(db_pool)
    
    # Auto join creator
    db_member = models.PoolMember(pool_id=db_pool.id, user_id=user.id)
    db.add(db_member)
    db.commit()
    
    db_pool.people_count = 1
    db_pool.creator_name = user.name
    db_pool.creator_phone = user.phone
    db_pool.participants = [schemas.PoolMemberResponse.model_validate(user)]
    return db_pool

@router.get("/", response_model=List[schemas.PoolListResponse])
def get_pools(
    source: Optional[str] = None,
    destination: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    # Base query for future pools
    query = db.query(models.Pool).filter(models.Pool.departure_time > func.now())
    
    if source:
        query = query.filter(models.Pool.source.ilike(f"%{source}%"))
    if destination:
        query = query.filter(models.Pool.destination.ilike(f"%{destination}%"))
        
    pools = query.order_by(models.Pool.departure_time.asc()).all()
    
    # Attach members and count
    result = []
    for pool in pools:
        members = db.query(models.PoolMember).filter(models.PoolMember.pool_id == pool.id).all()
        pool.people_count = len(members)
        
        creator = db.query(models.User).filter(models.User.id == pool.creator_id).first()
        if creator:
            pool.creator_name = creator.name
            pool.creator_phone = creator.phone
            
        participants = []
        for member in members:
            u = db.query(models.User).filter(models.User.id == member.user_id).first()
            if u:
                participants.append(schemas.PoolMemberResponse.model_validate(u))
        pool.participants = participants
        result.append(pool)
        
    return result

@router.get("/{pool_id}", response_model=schemas.PoolDetailResponse)
def get_pool(
    pool_id: int, 
    db: Session = Depends(database.get_db)
):
    pool = db.query(models.Pool).filter(models.Pool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
        
    members = db.query(models.PoolMember).filter(models.PoolMember.pool_id == pool.id).all()
    pool.people_count = len(members)
    
    # Add creator info
    creator = db.query(models.User).filter(models.User.id == pool.creator_id).first()
    if creator:
        pool.creator_name = creator.name
        pool.creator_phone = creator.phone
    
    participants = []
    for member in members:
        u = db.query(models.User).filter(models.User.id == member.user_id).first()
        if u:
            participants.append(schemas.PoolMemberResponse.model_validate(u))
    pool.participants = participants
        
    return pool

@router.post("/{pool_id}/join")
def join_pool(
    pool_id: int,
    join_in: schemas.PoolJoin,
    db: Session = Depends(database.get_db)
):
    try:
        user = get_or_create_user(db, join_in.user)
            
        pool = db.query(models.Pool).filter(models.Pool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
            
        # Compare using timezone-aware datetimes
        pool_dt = pool.departure_time
        if isinstance(pool_dt, str):
            pool_dt = datetime.fromisoformat(pool_dt.replace('Z', '+00:00'))
            
        if pool_dt.tzinfo is None:
            pool_dt = pool_dt.replace(tzinfo=timezone.utc)
            
        if pool_dt < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Cannot join past pools")
            
        # Check duplicate
        existing = db.query(models.PoolMember).filter(
            models.PoolMember.pool_id == pool_id,
            models.PoolMember.user_id == user.id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already joined this pool")
            
        new_member = models.PoolMember(pool_id=pool_id, user_id=user.id)
        db.add(new_member)
        db.commit()
        
        return {"message": "Successfully joined the pool"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error during join: {str(e)}")
