from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone

import models, schemas, database

router = APIRouter(prefix="/api/pools", tags=["pools"])


# ✅ Helper: Normalize any datetime to UTC safely
def to_utc(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

    if dt.tzinfo is None:
        # Assume stored as UTC in DB
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


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
        departure_time=to_utc(pool_in.departure_time),  # ✅ normalize here
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
    now_utc = datetime.now(timezone.utc)

    query = db.query(models.Pool).filter(
        models.Pool.departure_time > now_utc
    )

    if source:
        query = query.filter(models.Pool.source.ilike(f"%{source}%"))

    if destination:
        query = query.filter(models.Pool.destination.ilike(f"%{destination}%"))

    pools = query.order_by(models.Pool.departure_time.asc()).all()

    result = []

    for pool in pools:
        members = db.query(models.PoolMember).filter(
            models.PoolMember.pool_id == pool.id
        ).all()

        pool.people_count = len(members)

        creator = db.query(models.User).filter(
            models.User.id == pool.creator_id
        ).first()

        if creator:
            pool.creator_name = creator.name
            pool.creator_phone = creator.phone

        participants = []
        for member in members:
            u = db.query(models.User).filter(
                models.User.id == member.user_id
            ).first()

            if u:
                participants.append(
                    schemas.PoolMemberResponse.model_validate(u)
                )

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

    members = db.query(models.PoolMember).filter(
        models.PoolMember.pool_id == pool.id
    ).all()

    pool.people_count = len(members)

    creator = db.query(models.User).filter(
        models.User.id == pool.creator_id
    ).first()

    if creator:
        pool.creator_name = creator.name
        pool.creator_phone = creator.phone

    participants = []
    for member in members:
        u = db.query(models.User).filter(
            models.User.id == member.user_id
        ).first()

        if u:
            participants.append(
                schemas.PoolMemberResponse.model_validate(u)
            )

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

        # ✅ Safe UTC comparison
        pool_dt = to_utc(pool.departure_time)
        now_utc = datetime.now(timezone.utc)

        if pool_dt < now_utc:
            raise HTTPException(
                status_code=400,
                detail="Cannot join past pools"
            )

        # Check duplicate
        existing = db.query(models.PoolMember).filter(
            models.PoolMember.pool_id == pool_id,
            models.PoolMember.user_id == user.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Already joined this pool"
            )

        new_member = models.PoolMember(
            pool_id=pool_id,
            user_id=user.id
        )

        db.add(new_member)
        db.commit()

        return {"message": "Successfully joined the pool"}

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Server error during join: {str(e)}"
        )