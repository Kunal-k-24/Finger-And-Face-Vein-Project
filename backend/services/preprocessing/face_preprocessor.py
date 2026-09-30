import cv2
import torch
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from facenet_pytorch import MTCNN
from torchvision import transforms

class FacePreprocessor:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.mtcnn = MTCNN(
            image_size=160,
            margin=20,
            min_face_size=40,
            post_process=False,
            device=self.device
        )
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def preprocess_image(self, image_bytes: bytes) -> Tuple[torch.Tensor, bool]:
        """
        Detects, crops, aligns, applies CLAHE, and normalizes a face image.
        Returns (tensor_image [1, 3, 160, 160], success_flag).
        """
        try:
            # Decode bytes to OpenCV BGR
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_bgr is None:
                return torch.zeros((1, 3, 160, 160)), False

            # Convert to PIL Image for MTCNN
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # MTCNN crop & detect
            face_crop = self.mtcnn(pil_img)
            if face_crop is None:
                # Fallback to direct resize if face not detected by MTCNN
                resized = cv2.resize(img_rgb, (160, 160))
                pil_crop = Image.fromarray(resized)
            else:
                # Convert MTCNN tensor [3, 160, 160] back to uint8 image for CLAHE
                crop_np = face_crop.permute(1, 2, 0).cpu().numpy().astype(np.uint8)
                
                # Apply CLAHE on Y luminance channel
                yuv = cv2.cvtColor(crop_np, cv2.COLOR_RGB2YUV)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
                rgb_clahe = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
                pil_crop = Image.fromarray(rgb_clahe)

            # Transform to normalized tensor
            tensor_img = self.transform(pil_crop).unsqueeze(0)
            return tensor_img, True
        except Exception as e:
            print(f"[FacePreprocessor Error] {e}")
            return torch.zeros((1, 3, 160, 160)), False

face_preprocessor = FacePreprocessor()
