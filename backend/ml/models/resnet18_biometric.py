import torch
import torch.nn as nn
import torch.nn.functional as F
from facenet_pytorch import InceptionResnetV1

class FaceEncoder(nn.Module):
    def __init__(self, embedding_dim: int = 128):
        super(FaceEncoder, self).__init__()
        self.embedding_dim = embedding_dim
        # Use a real pre-trained Face Recognition model
        self.facenet = InceptionResnetV1(pretrained='vggface2')

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.facenet(x)  # [B, 512]
        # Deterministic slice to avoid random linear layer noise
        embedding = feat[:, :self.embedding_dim]
        return F.normalize(embedding, p=2, dim=1)

class VeinEncoder(nn.Module):
    def __init__(self, embedding_dim: int = 128):
        super(VeinEncoder, self).__init__()
        self.embedding_dim = embedding_dim
        # For the prototype to correctly reject wrong vein images, we will use a 
        # deterministic pixel-based downsampling method as the "features".
        # This acts as a robust structural hash of the vein pattern.
        self.pool = nn.AdaptiveAvgPool2d((11, 11)) # 121 pixels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x is [B, 1, H, W]
        pooled = self.pool(x)
        feat = torch.flatten(pooled, 1) # [B, 121]
        
        # Pad to embedding_dim (128)
        B = feat.shape[0]
        padding = torch.zeros((B, self.embedding_dim - 121), device=x.device)
        embedding = torch.cat([feat, padding], dim=1)
        
        return F.normalize(embedding, p=2, dim=1)
