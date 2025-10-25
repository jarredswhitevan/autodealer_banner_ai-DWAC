import io, os, requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from processors import resize_max_side, enhance_image
from utils import images_to_zip

# CONFIG
st.set_page_config(page_title="AutoDealer Banner AI", layout="wide")
st.title("🚗 AutoDealer Banner AI")
st.caption("Uploads → Background cleaned (via API) → Branded banners → Download-ready marketing images")

# ASSETS
BACKGROUND_PATH = "assets/dwa_building_clean.png"
FONT_BOLD = "assets/Roboto-Bold.ttf"
FONT_REGULAR = "assets/Roboto-Regular.ttf"

# -------- Background Removal (Cloud-Safe) --------
def remove_bg_online(img: Image.Image):
    """
    Uses the public rembg API endpoint to remove backgrounds.
    This version runs safely inside Streamlit Cloud.
    """
    url = "https://api.rembg.io"
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    try:
        response = requests.post(url, files={"image": buf.getvalue()})
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)).convert("RGBA")
        else:
            st.warning("⚠️ Background removal failed; showing original image.")
            return img.convert("RGBA")
    except Exception as e:
        st.warning(f"⚠️ Background removal failed: {e}")
        return img.convert("RGBA")

# -------- Sidebar Controls --------
with st.sidebar:
    st.header("Banner Settings")
    top_text = st.text_input("Top Banner (Year Make Model):", "2013 RAM 1500")
    dealer_name = "DAVE WHITE AUTO CREDIT"
    address = "5451 W Alexis Rd, Sylvania Ohio 43560"
    phone = "419-882-8736"
    st.write("---")
    st.markdown("**All banners stay red for brand consistency.**")
    st.write("Output: 1600×900 (optimized for web & Marketplace)")

# -------- Banner Builder --------
def add_banners(car_img: Image.Image, bg_img: Image.Image, top_text, address, phone, dealer_name):
    bg = bg_img.convert("RGB").resize((1600, 900))
    car_img = car_img.convert("RGBA")
    car_img = resize_max_side(car_img, 1000)
    w, h = car_img.size
    bg.paste(car_img, (int((bg.width - w)/2), int(bg.height - h*0.65)), car_img)
    draw = ImageDraw.Draw(bg)

    try:
        font_top = ImageFont.truetype(FONT_BOLD, 60)
        font_bottom = ImageFont.truetype(FONT_BOLD, 40)
        font_small = ImageFont.truetype(FONT_REGULAR, 36)
    except:
        font_top = font_bottom = font_small = ImageFont.load_default()

    # Top banner (red)
    banner_h = 100
    top_banner = Image.new("RGB", (bg.width, banner_h), (200, 0, 0))
    bg.paste(top_banner, (0, 0))
    draw.text((40, 15), top_text.upper(), font=font_top, fill="white")

    # Bottom banner (red)
    bh = 120
    bbar = Image.new("RGB", (bg.width, bh), (200, 0, 0))
    bg.paste(bbar, (0, bg.height - bh))
    draw.text((50, bg.height - 95), address, font=font_small, fill="white")
    draw.text((50, bg.height - 55), phone, font=font_bottom, fill="white")
    draw.text((900, bg.height - 85), dealer_name, font=font_bottom, fill="white")

    return bg

# -------- Processing Logic --------
def process_image(uploaded_file, bg_img):
    img = Image.open(uploaded_file).convert("RGB")
    img = resize_max_side(img, 2000)

    img = enhance_image(img)

    # use online background remover
    no_bg = remove_bg_online(img)

    return add_banners(no_bg, bg_img, top_text, address, phone, dealer_name)

# -------- Upload UI --------
files = st.file_uploader("Upload vehicle photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if files:
    bg_img = Image.open(BACKGROUND_PATH)
    cols = st.columns(3)
    results = []
    for i, f in enumerate(files):
        with cols[i % 3]:
            processed = process_image(f, bg_img)
            if processed is not None:
    st.image(processed, caption=f.name, use_container_width=True)
else:
    st.warning(f"⚠️ Failed to process {f.name}")

            results.append((f"{os.path.splitext(f.name)[0]}_branded.jpg", processed))

    if results:
        buf = images_to_zip(results, "branded.zip")
        st.download_button("⬇️ Download All (ZIP)", data=buf, file_name="branded.zip", mime="application/zip")
