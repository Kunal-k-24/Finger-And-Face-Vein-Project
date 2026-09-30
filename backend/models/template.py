import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class BiometricTemplate(Base):
    __tablename__ = "biometric_templates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # TenSEAL CKKS encrypted vector bytes
    encrypted_face_vector: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    encrypted_vein_vector: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    encrypted_fused_vector: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="templates")
