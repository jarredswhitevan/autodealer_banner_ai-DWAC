import cv2
import numpy as np
from PIL import Image

def pil_to_cv(img: Image.Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def cv_to_pil(img: np.ndarray):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def resize_max_side(img: Image.Image, max_side=2048):
    w, h = img.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return img
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

def auto_white_balance_cv(bgr):
    result = bgr.astype(np.float32)
    avg_b = np.mean(result[:, :, 0])
    avg_g = np.mean(result[:, :, 1])
    avg_r = np.mean(result[:, :, 2])
    avg_gray = (avg_b + avg_g + avg_r) / 3.0 + 1e-6
    result[:, :, 0] *= avg_gray / avg_b
    result[:, :, 1] *= avg_gray / avg_g
    result[:, :, 2] *= avg_gray / avg_r
    return np.clip(result, 0, 255).astype(np.uint8)

def clahe_contrast_cv(bgr, clip=3.0, tile=8):
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
    l2 = clahe.apply(l)
    lab2 = cv2.merge([l2, a, b])
    return cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)

def mild_sharpen_cv(bgr):
    blur = cv2.GaussianBlur(bgr, (0, 0), 1.2)
    sharp = cv2.addWeighted(bgr, 1.4, blur, -0.4, 0)
    return sharp
