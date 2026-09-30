import cv2
import torch
import numpy as np
from PIL import Image
from typing import Tuple
from torchvision import transforms

class VeinPreprocessor:
    def __init__(self, target_size: Tuple[int, int] = (160, 160)):
        self.target_size = target_size
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])  # Scale to [-1, 1]
        ])

    def preprocess_image(self, image_bytes: bytes) -> Tuple[torch.Tensor, bool]:
        """
        Process finger vein image:
        1. Decode image (grayscale)
        2. ROI cropping / edge detection
        3. Percentile intensity clipping
        4. CLAHE contrast enhancement
        5. Normalize to [-1, 1] for 1-channel network input
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_gray = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img_gray is None:
                return torch.zeros((1, 1, self.target_size[0], self.target_size[1])), False

            # Percentile intensity clipping
            p2, p98 = np.percentile(img_gray, (2, 98))
            clipped = np.clip(img_gray, p2, p98)
            norm_clipped = cv2.normalize(clipped, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

            # CLAHE contrast enhancement for vein patterns
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(norm_clipped)

            # Resize to target input size
            resized = cv2.resize(enhanced, self.target_size, interpolation=cv2.INTER_CUBIC)
            
            pil_img = Image.fromarray(resized)
            tensor_img = self.transform(pil_img).unsqueeze(0)  # Shape: [1, 1, 160, 160]
            return tensor_img, True
        except Exception as e:
            print(f"[VeinPreprocessor Error] {e}")
            return torch.zeros((1, 1, self.target_size[0], self.target_size[1])), False

vein_preprocessor = VeinPreprocessor()
