# Advanced QR Code Generator ✨

A powerful and user-friendly web application built with Python and Streamlit to create highly customized, professional-grade QR codes.

This tool goes beyond basic QR code generation, offering advanced design options for embedding logos with seamless integration, full color control, and precise QR parameter tuning. It's perfect for marketers, designers, developers, and anyone needing to create unique and attractive QR codes.



*(Note: The screenshot above is a representative example of the application's interface.)*

---

## Features

This application is packed with features to give you complete creative control:

### 🎨 Advanced Logo Integration
- **Upload Any Logo:** Easily upload your brand's logo (PNG, JPG, JPEG).
- **Multiple Logo Shapes:** Mask your logo into a **Square**, **Circle**, or a modern **Rounded Rectangle**.
- **Professional Background Styles:**
    - **Solid:** A clean, solid-colored frame behind the logo.
    - **Gradient Halo:** A stunning effect where the QR code modules smoothly fade out as they approach the logo, creating a soft, professional clearing.
    - **Radial Gradient:** A vibrant circular gradient behind the logo for an eye-catching effect.
- **Logo Border:** Add a crisp border around the logo that intelligently adapts to the chosen shape.

### ⚙️ Full QR Code Control
- **Error Correction Level (ECL):** Choose from Low, Medium, Quartile, or High levels. The app provides a warning if you use a logo without High ECL.
- **Version (Size) Control:** Specify the exact minimum and maximum QR code version to use.
- **Mask Pattern Selection:** Let the library auto-select the optimal mask for readability, or manually force one of the 8 patterns.
- **Boost ECC:** Automatically increase the error correction level if it can be done without increasing the QR version, making your code more robust for free.

### 🖌️ Styling and High-Resolution Output
- **Full Color Control:** Use color pickers to choose exact hex colors for both the QR code and its background.
- **Adjustable Module Size:** Control the pixel size of each square in the QR code, allowing you to generate high-resolution PNGs perfect for print and digital media.
- **Customizable Quiet Zone:** Adjust the width of the border (quiet zone) around the QR code.
- **Download as PNG:** Save your final creation as a high-quality PNG file with a single click.

---

## Setup and Installation

Follow these steps to get the application running on your local machine.

### Prerequisites
- Python 3.8 or newer
- `pip` (Python's package installer)

### 1. Get the Code
Download the project files and place them in a single project folder. Your folder should contain:
- `qr_code_app.py`
- `qrcodegen.py`
- `requirements.txt`

### 2. Create a Virtual Environment (Recommended)
It is highly recommended to use a virtual environment to keep project dependencies isolated.

Open your terminal or command prompt and navigate to the project directory:
```bash
# Create a virtual environment named '.venv'
python -m venv .venv
