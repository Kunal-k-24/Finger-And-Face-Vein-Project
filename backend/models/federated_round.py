import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base

class FederatedRound(Base):
    __tablename__ = "federated_rounds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    client_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    global_accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    global_loss: Mapped[float] = mapped_column(Float, nullable=True)
    epsilon: Mapped[float] = mapped_column(Float, nullable=True)  # DP privacy budget used
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
