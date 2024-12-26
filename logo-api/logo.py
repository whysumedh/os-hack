from flask import Flask, request, jsonify
from PIL import Image, ImageOps
import requests
from io import BytesIO
from google.cloud import storage
import os

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"

bucket_name = "os-api-assignment"

def upload_to_gcs(image: BytesIO, file_name: str) -> str:
    """Uploads an image to Google Cloud Storage and returns its public URL."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_file(image, content_type="image/png")
        blob.make_public()
        return blob.public_url
    except Exception as e:
        raise Exception(f"Failed to upload to GCS: {str(e)}")

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content)).convert("RGBA")
    else:
        raise Exception(f"Failed to download image from {url}")

def remove_background(image):
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] > 200 and item[1] > 200 and item[2] > 200:  
            new_data.append((255, 255, 255, 0)) 
        elif item[0] < 50 and item[1] < 50 and item[2] < 50: 
            new_data.append((255, 255, 255, 0)) 
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image

def calculate_luminance(color):
    r, g, b = color
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255

def recolor_logo(logo, base_image, brand_palette):
    logo_gray = logo.convert("L")
    dominant_color = base_image.resize((1, 1)).getpixel((0, 0))[:3]
    luminance = calculate_luminance(dominant_color)
    best_color = brand_palette[0] if luminance > 0.5 else brand_palette[1]
    recolored_logo = logo.convert("RGBA")
    datas = recolored_logo.getdata()
    new_data = []
    for item in datas:
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            r, g, b = [int(best_color[i:i+2], 16) for i in range(1, len(best_color), 2)]
            new_data.append((r, g, b, item[3]))
        else:
            new_data.append(item)
    recolored_logo.putdata(new_data)
    return recolored_logo

def resize_logo(logo, base_image, scale_factor=0.2):
    max_width = int(base_image.width * scale_factor)
    max_height = int(base_image.height * scale_factor)
    logo = logo.resize((max_width, max_height), Image.Resampling.LANCZOS)
    return logo

def paste_logo(base_image, logo, position):
    positions = {
        "top-left": (11, 11),
        "top-right": (base_image.width - logo.width - 10, 10),
        "bottom-left": (10, base_image.height - logo.height - 10),
        "bottom-right": (base_image.width - logo.width - 10, base_image.height - logo.height - 10)
    }
    if position not in positions:
        raise ValueError("Invalid position specified")
    base_image.paste(logo, positions[position], logo if "A" in logo.getbands() else None)
    return base_image

@app.route('/integrate_logo', methods=['POST'])
def integrate_logo_with_image():
    try:
        # Parse input JSON
        data = request.json
        base_image_url = data.get('base_image_url')
        logo_url = data.get('logo_url')
        brand_palette = data.get('brand_palette', ["#FFC107", "#212121"])
        position = data.get('position', 'top-right')
        scale_factor = float(data.get('scale_factor', 0.2))
        file_name = data.get('file_name', 'output_image.png')

        # Validate inputs
        if not base_image_url or not logo_url:
            return jsonify({'error': 'base_image_url and logo_url are required'}), 400

        # Process the images
        base_image = download_image(base_image_url)
        logo = download_image(logo_url)
        logo = remove_background(logo)
        logo = resize_logo(logo, base_image, scale_factor)
        logo = recolor_logo(logo, base_image, brand_palette)
        final_image = paste_logo(base_image, logo, position)

        # Save the image to a BytesIO object
        image_io = BytesIO()
        final_image.save(image_io, format="PNG")
        image_io.seek(0)

        # Upload to GCS and get public URL
        public_url = upload_to_gcs(image_io, file_name)

        return jsonify({'public_url': public_url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
