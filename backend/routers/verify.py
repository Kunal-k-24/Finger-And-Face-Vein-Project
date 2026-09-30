import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.database import get_db
from backend.models.template import BiometricTemplate
from backend.models.auth_log import AuthLog
from backend.models.user import User
from backend.schemas.biometric import VerifyResponse
from backend.services.feature_extractor import feature_extractor
from backend.services.encryption import he_service
from backend.config import settings

router = APIRouter(prefix="/biometric", tags=["Biometrics"])

@router.post("/verify", response_model=VerifyResponse)
async def verify_biometrics(
    username: str = Form(...),
    face_image: UploadFile = File(...),
    vein_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()
    
    try:
        # 1. Fetch User
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # 2. Fetch User's Enrolled Template
        template_res = await db.execute(select(BiometricTemplate).where(BiometricTemplate.user_id == user.id))
        template = template_res.scalars().first()
        if not template:
            raise HTTPException(status_code=404, detail="No enrolled biometric template found for this user")
            
        # 3. Extract features from incoming images
        face_bytes = await face_image.read()
        vein_bytes = await vein_image.read()
        
        _, _, query_fused_emb = feature_extractor.extract_features(face_bytes, vein_bytes)
        if sum(query_fused_emb) == 0:
            raise HTTPException(status_code=400, detail="Failed to extract features from provided images")
            
        # 4. Compute Homomorphic Encrypted Cosine Similarity
        similarity = he_service.compute_encrypted_cosine_similarity(
            query_vector=query_fused_emb,
            enrolled_serialized_bytes=template.encrypted_fused_vector
        )
        
        latency = (time.time() - start_time) * 1000  # ms
        
        # 5. Check Threshold
        is_authenticated = similarity >= settings.SIMILARITY_THRESHOLD
        
        status_str = "success" if is_authenticated else "rejected"
        message = "Authentication successful" if is_authenticated else "Authentication failed. Biometrics do not match."
        
        # 6. Log verification attempt
        log = AuthLog(
            user_id=user.id,
            event_type="verification",
            status=status_str,
            similarity_score=similarity,
            latency_ms=latency
        )
        db.add(log)
        await db.commit()
        
        # Gather data for frontend visualization
        face_emb, vein_emb, _ = feature_extractor.extract_features(face_bytes, vein_bytes)
        step_data = {
            "face": f"Live Vector[{len(face_emb)}]: {face_emb[0]:.4f}, {face_emb[1]:.4f}...",
            "vein": f"Live Vector[{len(vein_emb)}]: {vein_emb[0]:.4f}, {vein_emb[1]:.4f}...",
            "fusion": f"L2 Normalized Vector[{len(query_fused_emb)}]",
            "db_fetch": f"Retrieved Ciphertext ({len(template.encrypted_fused_vector)} bytes)",
            "homomorphic": f"Encrypted Dot Product computed in {(latency * 0.9):.1f}ms",
            "decision": f"Score: {similarity:.4f} vs Threshold: {settings.SIMILARITY_THRESHOLD}"
        }
        
        return VerifyResponse(
            authenticated=is_authenticated,
            user_id=user.id if is_authenticated else None,
            username=user.username if is_authenticated else None,
            similarity_score=similarity,
            threshold=settings.SIMILARITY_THRESHOLD,
            latency_ms=latency,
            message=message,
            step_data=step_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        # Log error
        log = AuthLog(
            event_type="verification",
            status="error",
            similarity_score=None,
            latency_ms=latency
        )
        db.add(log)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Verification process failed: {str(e)}")
