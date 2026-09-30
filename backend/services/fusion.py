import torch
import torch.nn.functional as F
import numpy as np
from typing import List, Union

class MultibiometricFusion:
    @staticmethod
    def fuse_embeddings(
        face_embedding: Union[torch.Tensor, np.ndarray, List[float]],
        vein_embedding: Union[torch.Tensor, np.ndarray, List[float]]
    ) -> List[float]:
        """
        Concatenates 128-d face embedding + 128-d vein embedding,
        and applies L2-normalization to produce a 256-d fused embedding vector.
        """
        if isinstance(face_embedding, list):
            face_embedding = np.array(face_embedding, dtype=np.float32)
        if isinstance(vein_embedding, list):
            vein_embedding = np.array(vein_embedding, dtype=np.float32)

        if isinstance(face_embedding, torch.Tensor):
            face_np = face_embedding.detach().cpu().squeeze().numpy()
        else:
            face_np = face_embedding.squeeze()

        if isinstance(vein_embedding, torch.Tensor):
            vein_np = vein_embedding.detach().cpu().squeeze().numpy()
        else:
            vein_np = vein_embedding.squeeze()

        # Concatenate into 256-d array
        fused = np.concatenate([face_np, vein_np], axis=0)

        # L2 Normalization
        norm = np.linalg.norm(fused)
        if norm > 0:
            fused = fused / norm

        return fused.tolist()

fusion_service = MultibiometricFusion()
