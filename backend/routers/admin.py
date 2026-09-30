from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.models.user import User
from backend.models.auth_log import AuthLog
from backend.models.federated_round import FederatedRound
from backend.schemas.admin import AdminMetricsResponse, AuthLogResponse, FederatedRoundResponse
from backend.services.authentication import get_current_user_payload

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

def verify_admin(payload: dict = Depends(get_current_user_payload)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return payload

@router.get("/metrics", response_model=AdminMetricsResponse, dependencies=[Depends(verify_admin)])
async def get_metrics(db: AsyncSession = Depends(get_db)):
    # Total Users
    users_count = await db.scalar(select(func.count(User.id)))
    
    # Enrollments
    enroll_count = await db.scalar(select(func.count(AuthLog.id)).where(AuthLog.event_type == "enrollment"))
    
    # Verifications
    verify_query = select(AuthLog).where(AuthLog.event_type == "verification")
    verify_res = await db.execute(verify_query)
    verifications = verify_res.scalars().all()
    
    verify_count = len(verifications)
    
    # Calculate FAR and FRR
    # FAR (False Acceptance Rate): impostor successfully verified (requires true labels, but we estimate based on 'success' if we assume impostor attacks, or we can mock it for now since we don't have labeled impostor attempts in DB yet)
    # Since we can't truly know FAR/FRR without ground truth, we'll return mock stats or calculated based on success/reject ratios.
    
    success_verifications = sum(1 for v in verifications if v.status == "success")
    rejected_verifications = sum(1 for v in verifications if v.status == "rejected")
    
    acceptance_rate = (success_verifications / verify_count * 100) if verify_count > 0 else 0.0
    
    # Avg latency
    total_latency = sum(v.latency_ms for v in verifications if v.latency_ms is not None)
    avg_latency = (total_latency / verify_count) if verify_count > 0 else 0.0
    
    return AdminMetricsResponse(
        total_users=users_count or 0,
        total_enrollments=enroll_count or 0,
        total_verifications=verify_count,
        far=0.01, # Mocked FAR
        frr=0.02, # Mocked FRR
        acceptance_rate=acceptance_rate,
        avg_latency_ms=avg_latency
    )

@router.get("/logs", response_model=List[AuthLogResponse], dependencies=[Depends(verify_admin)])
async def get_auth_logs(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuthLog).order_by(AuthLog.timestamp.desc()).limit(limit).offset(offset))
    logs = result.scalars().all()
    return logs

@router.get("/federated", response_model=List[FederatedRoundResponse], dependencies=[Depends(verify_admin)])
async def get_federated_rounds(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FederatedRound).order_by(FederatedRound.timestamp.desc()).limit(limit))
    rounds = result.scalars().all()
    return rounds
