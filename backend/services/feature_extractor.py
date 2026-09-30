import torch
from typing import Tuple, List, Optional
from backend.services.preprocessing.face_preprocessor import face_preprocessor
from backend.services.preprocessing.vein_preprocessor import vein_preprocessor
from backend.ml.models.resnet18_biometric import FaceEncoder, VeinEncoder
from backend.services.fusion import fusion_service

class FeatureExtractionService:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.face_encoder = FaceEncoder(embedding_dim=128).to(self.device)
        self.vein_encoder = VeinEncoder(embedding_dim=128).to(self.device)
        self.face_encoder.eval()
        self.vein_encoder.eval()

    def extract_features(
        self,
        face_bytes: Optional[bytes],
        vein_bytes: Optional[bytes]
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Extracts 128-d face embedding, 128-d vein embedding, and 256-d fused embedding.
        """
        with torch.no_grad():
            # Process Face
            if face_bytes:
                face_tensor, face_ok = face_preprocessor.preprocess_image(face_bytes)
                face_tensor = face_tensor.to(self.device)
                face_emb = self.face_encoder(face_tensor).squeeze().cpu().numpy().tolist()
            else:
                face_emb = [0.0] * 128

            # Process Vein
            if vein_bytes:
                vein_tensor, vein_ok = vein_preprocessor.preprocess_image(vein_bytes)
                vein_tensor = vein_tensor.to(self.device)
                vein_emb = self.vein_encoder(vein_tensor).squeeze().cpu().numpy().tolist()
            else:
                vein_emb = [0.0] * 128

            # Fuse embeddings into 256-d vector
            fused_emb = fusion_service.fuse_embeddings(face_emb, vein_emb)

            return face_emb, vein_emb, fused_emb

feature_extractor = FeatureExtractionService()
