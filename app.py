import io, os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
from utils import images_to_zip

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AutoDealer Banner AI", layout="wide")
st.title("🚗 AutoDealer Banner AI")
st.caption("Uploads → Cleaned backgrounds → Red dealership banners → Download-ready marketing images")

# ---------------- ASSETS ----------------
BACKGROUND_PATH = "assets/dwa_building_clean.png"
FONT_BOLD = "assets/Roboto-Bold.ttf"
FONT_REGULAR = "assets/Roboto-Regular.ttf"

# ---------------- IMAGE ENHANCEMENT ----------------
def resize_max_side(img: Image.Image, max_side=2048):
    w, h = img.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return img
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

def enhance_image(img: Image.Image):
    """Enhance color, contrast, and sharpness (no OpenCV needed)."""
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Color(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    return img

# ---------------- LOCAL BACKGROUND "REMOVAL" ----------------
def remove_bg_online(img: Image.Image):
    """
    Offline-safe fallback: light fade vignette to clean edges.
    Ensures app works even when external AI APIs are unreachable.
    """
    try:
        w, h = img.size
        fade = 80  # pixels of edge fade
        mask = Image.new("L", (w, h), 255)
        for i in range(fade):
            mask.paste(int(255 * (1 - i / fade)), (i, i, w - i, h - i))
        bg = Image.new("RGB", (w, h), (245, 245, 245))
        img = img.convert("RGB")
        bg.paste(img, (0, 0), mask)
        return bg.convert("RGBA")
    except Exception as e:
        st.warning(f"⚠️ Background fallback failed: {e}")
        return img.convert("RGBA")

# ---------------- SIDEBAR CONTROLS ----------------
with st.sidebar:
    st.header("Banner Settings")
    top_text = st.text_input("Top Banner (Year Make Model):", "2013 RAM 1500")
    dealer_name = "DAVE WHITE AUTO CREDIT"
    address = "5451 W Alexis Rd, Sylvania Ohio 43560"
    phone = "419-882-8736"
    st.write("---")
    st.markdown("**All banners stay red for brand consistency.**")
    st.write("Output size: 1600×900 (optimized for Marketplace & website)")

# ---------------- BANNER BUILDER ----------------
def add_banners(car_img: Image.Image, bg_img: Image.Image, top_text, address, phone, dealer_name):
    bg = bg_img.convert("RGB").resize((1600, 900))
    car_img = car_img.convert("RGBA")
    car_img = resize_max_side(car_img, 1000)
    w, h = car_img.size

    # Center car over background
    bg.paste(car_img, (int((bg.width - w)/2), int(bg.height - h*0.65)), car_img)
    draw = ImageDraw.Draw(bg)

    # Fonts
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

# ---------------- PROCESSING PIPELINE ----------------
def process_image(uploaded_file, bg_img):
    """Full enhancement + background cleanup + banner pipeline."""
    try:
        img = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.warning(f"⚠️ Could not open {uploaded_file.name}: {e}")
        return None

    img = resize_max_side(img, 2000)
    img = enhance_image(img)
    no_bg = remove_bg_online(img)
    result = add_banners(no_bg, bg_img, top_text, address, phone, dealer_name)
    return result

# ---------------- MAIN APP ----------------
files = st.file_uploader(
    "Upload vehicle photos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if files:
    try:
        bg_img = Image.open(BACKGROUND_PATH)
    except Exception as e:
        st.error(f"❌ Could not load dealership background ({BACKGROUND_PATH}): {e}")
        st.stop()

    cols = st.columns(3)
    results = []

    for i, f in enumerate(files):
        with cols[i % 3]:
            processed = process_image(f, bg_img)
            if processed is not None:
                st.image(processed, caption=f.name, use_container_width=True)
                results.append((f"{os.path.splitext(f.name)[0]}_branded.jpg", processed))
            else:
                st.warning(f"⚠️ Failed to process {f.name}")

    if results:
        buf = images_to_zip(results, "branded.zip")
        st.download_button(
            "⬇️ Download All (ZIP)",
            data=buf,
            file_name="branded.zip",
            mime="application/zip"
        )
else:
    st.info("👆 Upload your vehicle photos to begin.")
