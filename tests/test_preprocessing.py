import numpy as np
import cv2
from backend.services.feature_extractor import feature_extractor

def test_pipeline_preprocessing_and_extraction():
    # Create synthetic RGB face image (160x160x3)
    synthetic_face = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
    _, face_bytes = cv2.imencode('.jpg', synthetic_face)

    # Create synthetic Grayscale vein image (160x160)
    synthetic_vein = np.random.randint(0, 255, (160, 160), dtype=np.uint8)
    _, vein_bytes = cv2.imencode('.jpg', synthetic_vein)

    # Extract features
    face_emb, vein_emb, fused_emb = feature_extractor.extract_features(
        face_bytes.tobytes(),
        vein_bytes.tobytes()
    )

    print(f"[TEST] Face embedding dim: {len(face_emb)}")
    print(f"[TEST] Vein embedding dim: {len(vein_emb)}")
    print(f"[TEST] Fused embedding dim: {len(fused_emb)}")
    print(f"[TEST] Fused vector L2 norm: {np.linalg.norm(fused_emb):.4f}")

    assert len(face_emb) == 128
    assert len(vein_emb) == 128
    assert len(fused_emb) == 256
    assert np.isclose(np.linalg.norm(fused_emb), 1.0, atol=1e-3)
    print("ALL PREPROCESSING AND FEATURE EXTRACTION TESTS PASSED!")

if __name__ == "__main__":
    test_pipeline_preprocessing_and_extraction()
