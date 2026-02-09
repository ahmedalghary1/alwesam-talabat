import os
from PIL import Image


SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')


def convert_folder_images_to_webp(
    folder_path,
    quality=85
):
    """
    Convert all images in a folder to WebP format
    - Keep original dimensions
    - Compress image
    - Delete old image
    - Save new image with same name (.webp)
    """

    if not os.path.isdir(folder_path):
        raise ValueError("Invalid folder path")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        name, ext = os.path.splitext(filename)

        # Skip unsupported files or already webp
        if ext.lower() not in SUPPORTED_EXTENSIONS or ext.lower() == ".webp":
            continue

        try:
            img = Image.open(file_path)

            # Handle transparency
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Save as WebP (NO RESIZE)
            webp_path = os.path.join(folder_path, f"{name}.webp")
            img.save(
                webp_path,
                format="WEBP",
                quality=quality,
                method=6,
                optimize=True
            )

            # Remove old image
            os.remove(file_path)

            print(f"✔ Converted: {filename} → {name}.webp")

        except Exception as e:
            print(f"✖ Failed: {filename} | Error: {e}")


convert_folder_images_to_webp('.')