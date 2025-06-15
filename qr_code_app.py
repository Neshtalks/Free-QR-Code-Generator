import streamlit as st
from qrcodegen import QrCode, QrSegment, DataTooLongError
from PIL import Image, ImageDraw
import io
import numpy as np
import math

# --- Core Functions ---

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converts a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_qr_image(
    qr: QrCode, module_size: int, border: int, 
    light_color: tuple[int, int, int], dark_color: tuple[int, int, int], 
    logo_image: Image.Image = None, logo_options: dict = {}
):
    """Renders a QrCode object into a PIL Image with advanced logo integration."""
    image_size = (qr.get_size() + border * 2) * module_size
    
    # --- 1. Create the base QR Code Image ---
    if logo_options.get("background_style") == "Gradient Halo":
        # Halo effect requires an RGBA canvas for transparency
        img = Image.new("RGBA", (image_size, image_size), (*light_color, 255))
    else:
        img = Image.new("RGB", (image_size, image_size), light_color)

    pixels = img.load()
    for y in range(qr.get_size()):
        for x in range(qr.get_size()):
            if qr.get_module(x, y):
                for dy in range(module_size):
                    for dx in range(module_size):
                        pixels[(x + border) * module_size + dx, (y + border) * module_size + dy] = dark_color

    # --- 2. Handle Logo Integration ---
    if logo_image:
        logo_size_ratio = logo_options.get("size", 0.25)
        logo_max_size = int(image_size * logo_size_ratio)
        logo_image.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
        
        logo_x = (image_size - logo_image.width) // 2
        logo_y = (image_size - logo_image.height) // 2
        
        # --- 2a. Create the background for the logo ---
        if logo_options.get("background_style") == "Gradient Halo":
            # The halo is created by modifying the main image's alpha channel
            center_x, center_y = image_size / 2, image_size / 2
            outer_radius = (max(logo_image.size) / 2) + (module_size * 2)
            inner_radius = max(logo_image.size) / 2
            
            x_coords, y_coords = np.meshgrid(np.arange(image_size), np.arange(image_size))
            distances = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            
            alpha_mask = np.ones((image_size, image_size), dtype=np.uint8) * 255
            fade_zone = (distances > inner_radius) & (distances < outer_radius)
            alpha_mask[fade_zone] = (255 * (distances[fade_zone] - inner_radius) / (outer_radius - inner_radius)).astype(np.uint8)
            alpha_mask[distances <= inner_radius] = 0
            
            img.putalpha(Image.fromarray(alpha_mask, 'L'))

        elif logo_options.get("background_style") == "Radial Gradient":
            grad_size = int(max(logo_image.size) * 1.2)
            grad_img = Image.new("RGB", (grad_size, grad_size))
            draw = ImageDraw.Draw(grad_img)
            
            for i in range(grad_size):
                ratio = i / grad_size
                r = int(light_color[0] * ratio + dark_color[0] * (1 - ratio))
                g = int(light_color[1] * ratio + dark_color[1] * (1 - ratio))
                b = int(light_color[2] * ratio + dark_color[2] * (1 - ratio))
                draw.ellipse((i, i, grad_size - i - 1, grad_size - i - 1), fill=(r,g,b))
            img.paste(grad_img, ((image_size - grad_size)//2, (image_size - grad_size)//2))

        # --- 2b. Prepare logo shape and border ---
        logo_shape = logo_options.get("shape", "Square")
        
        # Create mask for the chosen shape
        logo_mask = Image.new('L', logo_image.size, 0)
        draw = ImageDraw.Draw(logo_mask)
        if logo_shape == "Circle":
            draw.ellipse((0, 0) + logo_image.size, fill=255)
        elif logo_shape == "Rounded Rectangle":
            corner_radius = int(min(logo_image.size) * 0.2)
            draw.rounded_rectangle((0, 0) + logo_image.size, radius=corner_radius, fill=255)
        else: # Square
            draw.rectangle((0, 0) + logo_image.size, fill=255)

        # Add border if requested
        if logo_options.get("border", False):
            border_width = max(1, int(module_size * 0.75))
            border_frame_size = (logo_image.width + border_width*2, logo_image.height + border_width*2)
            
            border_mask = Image.new('L', border_frame_size, 0)
            draw = ImageDraw.Draw(border_mask)
            
            if logo_shape == "Circle":
                draw.ellipse((0, 0) + border_frame_size, fill=255)
            elif logo_shape == "Rounded Rectangle":
                corner_radius = int(min(border_frame_size) * 0.2)
                draw.rounded_rectangle((0, 0) + border_frame_size, radius=corner_radius, fill=255)
            else:
                draw.rectangle((0, 0) + border_frame_size, fill=255)

            frame = Image.new("RGBA" if img.mode == 'RGBA' else "RGB", border_frame_size, dark_color)
            img.paste(frame, (logo_x - border_width, logo_y - border_width), border_mask)

        # --- 2c. Paste the final logo ---
        img.paste(logo_image, (logo_x, logo_y), logo_mask)
    
    # Convert back to RGB for saving as PNG if it was RGBA
    if img.mode == 'RGBA':
        rgb_img = Image.new("RGB", img.size, light_color)
        rgb_img.paste(img, (0,0), img)
        return rgb_img
        
    return img


# --- Streamlit App ---
def main():
    st.set_page_config(page_title="Advanced QR Code Generator", page_icon="🔗", layout="centered")
    st.title("Advanced QR Code Generator")
    st.write("Create highly customized QR codes with logos and advanced design settings.")

    with st.sidebar:
        st.header("Customization Options")

        st.subheader("1. Content")
        text_input = st.text_area("Enter the text or URL to encode:", "https://www.uacrdc.com/", height=100)

        st.subheader("2. QR Code Settings")
        ecl_choice = st.selectbox("Error Correction Level", ["Low (L)", "Medium (M)", "Quartile (Q)", "High (H)"], index=3, help="Higher levels are more robust but store less data. 'High' is recommended for QR codes with logos.")
        ecl_map = {"Low (L)": QrCode.Ecc.LOW, "Medium (M)": QrCode.Ecc.MEDIUM, "Quartile (Q)": QrCode.Ecc.QUARTILE, "High (H)": QrCode.Ecc.HIGH}
        ecl = ecl_map[ecl_choice]

        with st.expander("Advanced QR Settings"):
            min_version, max_version = st.slider("QR Code Version (Size)", 1, 40, (1, 40))
            mask_options = {"Auto": -1, "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7}
            mask_choice = st.selectbox("Mask Pattern", list(mask_options.keys()), index=0)
            mask = mask_options[mask_choice]
            boost_ecl = st.checkbox("Boost Error Correction", True, help="Automatically increase ECC level if it doesn't increase QR version.")

        st.subheader("3. Logo")
        uploaded_logo = st.file_uploader("Upload a logo image", type=["png", "jpg", "jpeg"])
        
        with st.expander("Logo Styling Options", expanded=True):
            logo_size = st.slider("Logo Size", 5, 40, 25, help="Percentage of the QR code the logo will occupy.") / 100.0
            logo_shape = st.selectbox("Logo Shape", ["Square", "Circle", "Rounded Rectangle"])
            logo_bg_style = st.selectbox("Logo Background Style", ["Solid", "Gradient Halo", "Radial Gradient"], help="'Gradient Halo' provides the smoothest integration.")
            add_logo_border = st.checkbox("Add border to logo")

        st.subheader("4. Colors & Sizing")
        dark_color_hex = st.color_picker("QR Code Color", "#000000")
        light_color_hex = st.color_picker("Background Color", "#FFFFFF")
        border = st.number_input("Border (Quiet Zone)", 1, 20, 4)
        module_size = st.number_input("Module Size (pixels)", 2, 30, 15, help="Increase for higher resolution images.")

    if not text_input:
        st.warning("Please enter some text or a URL to get started.")
        st.stop()

    logo_image = Image.open(uploaded_logo) if uploaded_logo else None
    if logo_image and ecl_choice != "High (H)":
        st.warning("⚠️ **Warning:** Using a logo without 'High' Error Correction may make the QR code unscannable.")

    try:
        segs = QrSegment.make_segments(text_input)
        qr = QrCode.encode_segments(segs, ecl, min_version, max_version, mask, boost_ecl)
        
        logo_opts = {
            "size": logo_size, "shape": logo_shape, 
            "background_style": logo_bg_style, "border": add_logo_border
        }
        
        qr_image = create_qr_image(qr, module_size, border, hex_to_rgb(light_color_hex), hex_to_rgb(dark_color_hex), logo_image, logo_opts)
        
        st.image(qr_image, caption=f"Generated QR Code for: '{text_input}'", use_container_width=True)

        img_byte_arr = io.BytesIO()
        qr_image.save(img_byte_arr, format='PNG')
        
        st.download_button("⬇️ Download QR Code (PNG)", img_byte_arr.getvalue(), "custom_qrcode.png", "image/png")
        
        with st.expander("See generated QR code details"):
            st.info(f"Version: {qr.get_version()}\n\nSize: {qr.get_size()}x{qr.get_size()} modules\n\nError Correction Level: {ecl_choice}\n\nMask Pattern: {qr.get_mask()}")

    except DataTooLongError:
        st.error("❌ **Error:** The data is too long. Please enter less text or increase the maximum QR version.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()