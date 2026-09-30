import numpy as np
from backend.services.encryption import he_service

def test_homomorphic_encryption_similarity():
    # Generate 256-d normalized vector A
    vec_a = np.random.randn(256)
    vec_a /= np.linalg.norm(vec_a)
    
    # Generate vector B (identical to A for similarity = 1.0)
    vec_b = vec_a.copy()

    # Generate vector C (different for lower similarity)
    vec_c = np.random.randn(256)
    vec_c /= np.linalg.norm(vec_c)

    # Encrypt vector A
    enc_bytes_a = he_service.encrypt_vector(vec_a.tolist())

    # Compute encrypted cosine similarity with identical vector B
    sim_ab = he_service.compute_encrypted_cosine_similarity(vec_b.tolist(), enc_bytes_a)
    print(f"[TEST] Identical vector encrypted similarity: {sim_ab:.4f}")
    assert np.isclose(sim_ab, 1.0, atol=1e-3)

    # Compute encrypted cosine similarity with different vector C
    sim_ac = he_service.compute_encrypted_cosine_similarity(vec_c.tolist(), enc_bytes_a)
    print(f"[TEST] Different vector encrypted similarity: {sim_ac:.4f}")
    assert sim_ac < 0.9

    print("ALL HOMOMORPHIC ENCRYPTION TESTS PASSED!")

if __name__ == "__main__":
    test_homomorphic_encryption_similarity()
