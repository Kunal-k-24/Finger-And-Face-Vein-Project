import torch
from torch.utils.data import DataLoader
from opacus import PrivacyEngine
from typing import Tuple
from backend.config import settings

class DifferentialPrivacyService:
    def __init__(self):
        self.privacy_engine = PrivacyEngine()
        
    def make_private(self, module: torch.nn.Module, optimizer: torch.optim.Optimizer, data_loader: DataLoader) -> Tuple[torch.nn.Module, torch.optim.Optimizer, DataLoader]:
        """
        Attaches the Opacus PrivacyEngine to the model, optimizer, and data_loader 
        to ensure DP-SGD training.
        """
        try:
            model, optimizer, data_loader = self.privacy_engine.make_private(
                module=module,
                optimizer=optimizer,
                data_loader=data_loader,
                noise_multiplier=1.0, # You can calculate this based on target epsilon
                max_grad_norm=settings.DP_MAX_GRAD_NORM,
            )
            return model, optimizer, data_loader
        except Exception as e:
            print(f"[DP Service Error] Failed to attach PrivacyEngine: {e}")
            raise

    def get_privacy_spent(self) -> Tuple[float, float]:
        """
        Returns the privacy budget (epsilon, delta) spent so far.
        """
        try:
            epsilon = self.privacy_engine.get_epsilon(delta=settings.DP_TARGET_DELTA)
            return epsilon, settings.DP_TARGET_DELTA
        except Exception as e:
            print(f"[DP Service Error] Failed to compute privacy spent: {e}")
            return 0.0, settings.DP_TARGET_DELTA

dp_service = DifferentialPrivacyService()
