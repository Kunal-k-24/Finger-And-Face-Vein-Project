from pydantic import BaseModel
from typing import Optional

class VerifyResponse(BaseModel):
    authenticated: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    similarity_score: float
    threshold: float
    latency_ms: float
    message: str
    step_data: Optional[dict] = None

class EnrollResponse(BaseModel):
    success: bool
    template_id: str
    user_id: str
    message: str
    step_data: Optional[dict] = None

