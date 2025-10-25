from PIL import Image, ImageEnhance, ImageOps

def resize_max_side(img: Image.Image, max_side=2048):
    w, h = img.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return img
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

def enhance_image(img: Image.Image):
    """Approximate white balance, contrast, and sharpening without cv2."""
    img = ImageOps.autocontrast(img)                     # contrast stretch
    img = ImageEnhance.Color(img).enhance(1.15)          # richer colors
    img = ImageEnhance.Contrast(img).enhance(1.1)        # bump contrast
    img = ImageEnhance.Sharpness(img).enhance(1.2)       # subtle sharpen
    return img
