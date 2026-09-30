import tenseal as ts
import numpy as np
from typing import List, Tuple
from backend.config import settings

class HomomorphicEncryptionService:
    def __init__(self):
        # Create CKKS Homomorphic Encryption Context
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=settings.HE_POLY_MODULUS_DEGREE,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        self.context.global_scale = 2**40
        self.context.generate_galois_keys()

    def get_serialized_context(self) -> bytes:
        """Serialize context for transmission/storage."""
        return self.context.serialize()

    def encrypt_vector(self, vector: List[float]) -> bytes:
        """Encrypt a 1D float vector into serialized TenSEAL CKKS vector bytes."""
        enc_vec = ts.ckks_vector(self.context, vector)
        return enc_vec.serialize()

    def decrypt_vector(self, serialized_bytes: bytes) -> List[float]:
        """Decrypt serialized TenSEAL CKKS bytes into float list."""
        enc_vec = ts.ckks_vector_from(self.context, serialized_bytes)
        return enc_vec.decrypt()

    def compute_encrypted_cosine_similarity(
        self,
        query_vector: List[float],
        enrolled_serialized_bytes: bytes
    ) -> float:
        """
        Calculates similarity between a cleartext query vector (L2-normalized)
        and an encrypted enrolled vector (L2-normalized).
        Since vectors are L2-normalized, Cosine Similarity == Dot Product.
        """
        enc_enrolled = ts.ckks_vector_from(self.context, enrolled_serialized_bytes)
        # Encrypted dot product
        enc_dot = enc_enrolled.dot(query_vector)
        # Decrypt dot product result scalar
        similarity = enc_dot.decrypt()[0]
        return float(np.clip(similarity, -1.0, 1.0))

# Global singleton instance
he_service = HomomorphicEncryptionService()
