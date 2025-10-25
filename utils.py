import io, zipfile
from PIL import Image

def images_to_zip(named_images, zip_name="export.zip"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, img in named_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=92, optimize=True)
            z.writestr(name, img_bytes.getvalue())
    buf.seek(0)
    return buf
