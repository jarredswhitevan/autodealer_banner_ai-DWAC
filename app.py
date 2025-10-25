import io, os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from processors import resize_max_side, pil_to_cv, cv_to_pil, auto_white_balance_cv, clahe_contrast_cv, mild_sharpen_cv
from utils import images_to_zip

# CONFIG
st.set_page_config(page_title="AutoDealer Banner AI", layout="wide")
st.title("🚗 AutoDealer Banner AI")
st.caption("Uploads → Background cleaned → Branded banners → Download-ready marketing images")

# ASSETS
BACKGROUND_PATH = "assets/dwa_building_clean.png"
FONT_BOLD = "assets/Roboto-Bold.ttf"
FONT_REGULAR = "assets/Roboto-Regular.ttf"

# SIDEBAR SETTINGS
with st.sidebar:
    st.header("Banner Settings")
    top_text = st.text_input("Top Banner (Year Make Model):", "2013 RAM 1500")
    dealer_name = "DAVE WHITE AUTO CREDIT"
    address = "5451 W Alexis Rd, Sylvania Ohio 43560"
    phone = "419-882-8736"
    st.write("---")
    st.markdown("**All banners stay red for brand consistency.**")
    st.write("Output: 1600×900 (optimized for web & Marketplace)")

# FUNCTIONS
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
    # Top Banner
    banner_h = 100
    top_banner = Image.new("RGB", (bg.width, banner_h), (200, 0, 0))
    bg.paste(top_banner, (0, 0))
    draw.text((40, 15), top_text.upper(), font=font_top, fill="white")
    # Bottom Banner
    bh = 120
    bbar = Image.new("RGB", (bg.width, bh), (200, 0, 0))
    bg.paste(bbar, (0, bg.height - bh))
    draw.text((50, bg.height - 95), address, font=font_small, fill="white")
    draw.text((50, bg.height - 55), phone, font=font_bottom, fill="white")
    draw.text((900, bg.height - 85), dealer_name, font=font_bottom, fill="white")
    return bg

def process_image(uploaded_file, bg_img):
    img = Image.open(uploaded_file).convert("RGB")
    img = resize_max_side(img, 2000)
    cv = pil_to_cv(img)
    cv = auto_white_balance_cv(cv)
    cv = clahe_contrast_cv(cv)
    cv = mild_sharpen_cv(cv)
    img = cv_to_pil(cv)
    no_bg = Image.open(io.BytesIO(remove(img.tobytes()))).convert("RGBA")
    return add_banners(no_bg, bg_img, top_text, address, phone, dealer_name)

# UPLOAD SECTION
files = st.file_uploader("Upload vehicle photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if files:
    bg_img = Image.open(BACKGROUND_PATH)
    cols = st.columns(3)
    results = []
    for i, f in enumerate(files):
        with cols[i % 3]:
            processed = process_image(f, bg_img)
            st.image(processed, caption=f.name, use_container_width=True)
            results.append((f"{os.path.splitext(f.name)[0]}_branded.jpg", processed))
    if results:
        buf = images_to_zip(results, "branded.zip")
        st.download_button("⬇️ Download All (ZIP)", data=buf, file_name="branded.zip", mime="application/zip")
