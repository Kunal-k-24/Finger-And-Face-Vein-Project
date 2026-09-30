from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class AdminMetricsResponse(BaseModel):
    total_users: int
    total_enrollments: int
    total_verifications: int
    far: float  # False Acceptance Rate
    frr: float  # False Rejection Rate
    acceptance_rate: float
    avg_latency_ms: float

class AuthLogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    event_type: str
    status: str
    similarity_score: Optional[float]
    latency_ms: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True

class FederatedRoundResponse(BaseModel):
    id: str
    round_number: int
    client_count: int
    global_accuracy: Optional[float]
    global_loss: Optional[float]
    epsilon: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True
