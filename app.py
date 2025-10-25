import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from processors import (
    resize_max_side, pil_to_cv, cv_to_pil,
    auto_white_balance_cv, clahe_contrast_cv, mild_sharpen_cv
)
from utils import images_to_zip

st.set_page_config(page_title="AutoDealer Banner AI", layout="wide")
st.title("AutoDealer Banner AI")
st.caption("Upload any car photo → get dealership-branded marketing image automatically.")

# --- CONFIG ---
BACKGROUND_PATH = "assets/dwa_building_clean.png"   # <== put your cleaned dealership photo here
FONT_BOLD = "assets/Roboto-Bold.ttf"
FONT_REGULAR = "assets/Roboto-Regular.ttf"

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Banner Settings")
    year_make_model = st.text_input("Top Banner Text (e.g., 2018 Dodge Charger)", "2013 Toyota Venza")
    dealer_name = "DAVE WHITE AUTO CREDIT"
    address = "5451 W Alexis Rd, Sylvania Ohio 43560"
    phone = "419-882-8736"

    bg_color = (245, 245, 245)
    st.write("---")
    st.markdown("**Output size:** 1600×900 (optimized for Facebook/website)")

# --- FUNCTIONS ---
def add_banners(car_img: Image.Image, bg_img: Image.Image):
    """Place car over dealership background and add top/bottom banners."""
    bg = bg_img.convert("RGB").resize((1600, 900))
    car_img = car_img.convert("RGBA")
    car_img = resize_max_side(car_img, 1000)
    w, h = car_img.size
    bg.paste(car_img, (int((bg.width - w)/2), int(bg.height - h * 0.65)), car_img)

    draw = ImageDraw.Draw(bg)

    # --- FONTS ---
    try:
        font_top = ImageFont.truetype(FONT_BOLD, 60)
        font_bottom = ImageFont.truetype(FONT_BOLD, 40)
        font_small = ImageFont.truetype(FONT_REGULAR, 36)
    except:
        font_top = font_bottom = font_small = ImageFont.load_default()

    # --- TOP BANNER (RED ANGLED) ---
    banner_h = 100
    banner = Image.new("RGB", (bg.width, banner_h), (200, 0, 0))
    bg.paste(banner, (0, 0))
    draw.text((40, 15), year_make_model.upper(), font=font_top, fill="white")

    # --- BOTTOM BANNER (RED BACKGROUND) ---
    bh = 120
    bbar = Image.new("RGB", (bg.width, bh), (200, 0, 0))
    bg.paste(bbar, (0, bg.height - bh))
    draw.text((50, bg.height - 95), address, font=font_small, fill="white")
    draw.text((50, bg.height - 55), f"{phone}", font=font_bottom, fill="white")
    draw.text((900, bg.height - 85), dealer_name, font=font_bottom, fill="white")

    return bg

def process_car_image(uploaded_file, bg_img):
    img = Image.open(uploaded_file).convert("RGB")
    img = resize_max_side(img, 2000)
    cv = pil_to_cv(img)
    cv = auto_white_balance_cv(cv)
    cv = clahe_contrast_cv(cv)
    cv = mild_sharpen_cv(cv)
    img = cv_to_pil(cv)

    # remove background
    no_bg = Image.open(io.BytesIO(remove(img.tobytes()))).convert("RGBA")
    result = add_banners(no_bg, bg_img)
    return result

# --- MAIN UPLOAD ---
files = st.file_uploader("Upload vehicle photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if files:
    bg_img = Image.open(BACKGROUND_PATH)
    outputs = []
    cols = st.columns(3)
    for i, f in enumerate(files):
        with cols[i % 3]:
            result = process_car_image(f, bg_img)
            st.image(result, caption=f"{f.name}", use_container_width=True)
            outputs.append((f"{os.path.splitext(f.name)[0]}_bannered.jpg", result))

    if outputs:
        buf = images_to_zip(outputs, "branded.zip")
        st.download_button("⬇️ Download Branded Photos (ZIP)", buf, "branded.zip", "application/zip")
