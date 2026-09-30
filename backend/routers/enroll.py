from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.database import get_db
from backend.models.template import BiometricTemplate
from backend.models.auth_log import AuthLog
from backend.schemas.biometric import EnrollResponse
from backend.services.authentication import get_current_user_payload
from backend.services.feature_extractor import feature_extractor
from backend.services.encryption import he_service

router = APIRouter(prefix="/biometric", tags=["Biometrics"])

@router.post("/enroll", response_model=EnrollResponse)
async def enroll_biometrics(
    face_image: UploadFile = File(...),
    vein_image: UploadFile = File(...),
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    
    try:
        # Read bytes
        face_bytes = await face_image.read()
        vein_bytes = await vein_image.read()
        
        # Extract features
        face_emb, vein_emb, fused_emb = feature_extractor.extract_features(face_bytes, vein_bytes)
        
        # Check if embeddings are valid (not all zeros)
        if sum(fused_emb) == 0:
             raise HTTPException(status_code=400, detail="Failed to extract features from provided images.")

        # Encrypt the fused vector
        encrypted_fused = he_service.encrypt_vector(fused_emb)
        
        # We can also encrypt individual vectors if needed, but fused is the primary one
        encrypted_face = he_service.encrypt_vector(face_emb)
        encrypted_vein = he_service.encrypt_vector(vein_emb)
        
        template_id = str(uuid.uuid4())
        new_template = BiometricTemplate(
            id=template_id,
            user_id=user_id,
            encrypted_face_vector=encrypted_face,
            encrypted_vein_vector=encrypted_vein,
            encrypted_fused_vector=encrypted_fused
        )
        
        db.add(new_template)
        
        # Log enrollment
        log = AuthLog(
            user_id=user_id,
            event_type="enrollment",
            status="success",
            similarity_score=None,
            latency_ms=0.0
        )
        db.add(log)
        
        await db.commit()
        
        # Gather data for frontend visualization
        step_data = {
            "face": f"Vector[{len(face_emb)}]: {face_emb[0]:.4f}, {face_emb[1]:.4f}...",
            "vein": f"Vector[{len(vein_emb)}]: {vein_emb[0]:.4f}, {vein_emb[1]:.4f}...",
            "fusion": f"L2 Normalized Vector[{len(fused_emb)}]",
            "encryption": f"Ciphertext Size: {len(encrypted_fused)} bytes",
            "storage": f"Template ID: {template_id[:8]}..."
        }
        
        return EnrollResponse(
            success=True,
            template_id=template_id,
            user_id=user_id,
            message="Biometric enrollment successful.",
            step_data=step_data
        )

    except Exception as e:
        # Log failure
        log = AuthLog(
            user_id=user_id,
            event_type="enrollment",
            status="error",
            similarity_score=None,
            latency_ms=0.0
        )
        db.add(log)
        await db.commit()
        
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")
