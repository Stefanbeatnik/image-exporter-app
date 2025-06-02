import streamlit as st
from PIL import Image
import io
import zipfile
import os

def crop_to_ratio(img, target_ratio):
    width, height = img.size
    img_ratio = width / height
    target = target_ratio[0] / target_ratio[1]
    if img_ratio > target:
        # Crop width
        new_width = int(height * target)
        offset = (width - new_width) // 2
        box = (offset, 0, offset + new_width, height)
    else:
        # Crop height
        new_height = int(width / target)
        offset = (height - new_height) // 2
        box = (0, offset, width, offset + new_height)
    return img.crop(box)

st.title("Batch Art Exporter (Aspect Ratio & DPI)")

uploaded_file = st.file_uploader("Choose a JPEG or PNG file", type=["jpg", "jpeg", "png"])
ratios_input = st.text_input("Aspect Ratios (e.g. 3:2, 4:3, 5:4)", value="3:2, 5:4, 4:3")
dpis_input = st.text_input("DPI values (e.g. 300, 240, 150)", value="300, 240, 150")

if uploaded_file and st.button("Process"):
    try:
        aspect_ratios = []
        for ratio in ratios_input.split(","):
            parts = ratio.strip().split(":")
            if len(parts) != 2:
                raise ValueError
            aspect_ratios.append((int(parts[0]), int(parts[1])))
        dpi_values = [int(x.strip()) for x in dpis_input.split(",")]
        img = Image.open(uploaded_file)
        zip_buffer = io.BytesIO()
        filename_base = os.path.splitext(uploaded_file.name)[0]
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for ratio in aspect_ratios:
                cropped = crop_to_ratio(img, ratio)
                for dpi in dpi_values:
                    # JPEG Export
                    img_bytes_jpg = io.BytesIO()
                    name_jpg = f"{filename_base}_{ratio[0]}x{ratio[1]}_{dpi}dpi.jpg"
                    cropped.convert("RGB").save(img_bytes_jpg, format="JPEG", quality=95, dpi=(dpi, dpi))
                    img_bytes_jpg.seek(0)
                    zipf.writestr(name_jpg, img_bytes_jpg.read())
                    # PNG Export
                    img_bytes_png = io.BytesIO()
                    name_png = f"{filename_base}_{ratio[0]}x{ratio[1]}_{dpi}dpi.png"
                    cropped.save(img_bytes_png, format="PNG", dpi=(dpi, dpi))
                    img_bytes_png.seek(0)
                    zipf.writestr(name_png, img_bytes_png.read())
        zip_buffer.seek(0)
        st.success("Done! Download your images below.")
        st.download_button("Download ZIP", data=zip_buffer, file_name="exported_images.zip", mime="application/zip")
    except Exception as e:
        st.error(f"Error: {e}")
