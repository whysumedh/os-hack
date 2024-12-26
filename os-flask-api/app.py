
from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
import requests
import datetime
from rembg import remove
from google.cloud import storage, vision
from google.oauth2 import service_account
import os

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
storage_client = storage.Client()
bucket_name = "os-api-assignment"

credentials = service_account.Credentials.from_service_account_file("creds.json")
vision_client = vision.ImageAnnotatorClient(credentials=credentials)


@app.route("/remove-background", methods=["POST"])
def remove_background():
    try:
        # Parse input JSON
        data = request.json
        image_url = data.get("image_url")
        use_vision_api = data.get("vision-api", "false").lower() == "true"

        if not image_url:
            return jsonify({"error": "Image URL is required"}), 400

        # Fetch the image from the provided URL
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Unable to fetch image from URL"}), 400

        image = Image.open(BytesIO(response.content)).convert("RGBA")

        if use_vision_api:
            # Process using Vision API
            localized_objects = detect_objects_vision_api(image_url, image.width, image.height)
            object_urls = []
            for idx, obj in enumerate(localized_objects):
                bounding_box = obj["bounding_box"]

                # Crop the object from the original image
                obj_image = image.crop((
                    bounding_box["x_min"],
                    bounding_box["y_min"],
                    bounding_box["x_max"],
                    bounding_box["y_max"]
                ))

                # Save cropped object to buffer
                cropped_buffer = BytesIO()
                obj_image.save(cropped_buffer, format="PNG")
                cropped_buffer.seek(0)

                # Upload to GCS
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                file_name = f"object_{idx+1}_{obj['name']}_{timestamp}.png"
                object_url = upload_to_gcs(cropped_buffer, file_name)
                object_urls.append({"object_name": obj["name"], "url": object_url})

            return jsonify({
                "message": "Objects processed with Vision API.",
                "objects": object_urls
            }), 200
        else:
            # Process with Rembg
            bounding_box = data.get("bounding_box", None)
            if bounding_box is None:
                bounding_box = {"x_min": 0, "y_min": 0, "x_max": image.width, "y_max": image.height}

            x_min = bounding_box["x_min"]
            y_min = bounding_box["y_min"]
            x_max = bounding_box.get("x_max", image.width)
            y_max = bounding_box.get("y_max", image.height)

            x_max = min(x_max, image.width)
            y_max = min(y_max, image.height)
            x_min = max(x_min, 0)
            y_min = max(y_min, 0)

            cropped_image = image.crop((x_min, y_min, x_max, y_max))
            buffer = BytesIO()
            processed_image = remove(cropped_image)
            processed_image.save(buffer, format="PNG")
            buffer.seek(0)

            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"processed_image_{x_min}_{y_min}_{x_max}_{y_max}_{timestamp}.png"
            processed_image_url = upload_to_gcs(buffer, file_name)

            return jsonify({
                "original_image_url": image_url,
                "processed_image_url": processed_image_url
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def detect_objects_vision_api(image_url, width, height):
    """Detects objects in the image using Google Vision API."""
    response = requests.get(image_url)
    content = response.content

    image = vision.Image(content=content)
    response = vision_client.object_localization(image=image)
    objects = response.localized_object_annotations

    localized_objects = []
    for obj in objects:
        box = obj.bounding_poly.normalized_vertices
        bounding_box = {
            "x_min": int(min(vertex.x for vertex in box) * width),
            "y_min": int(min(vertex.y for vertex in box) * height),
            "x_max": int(max(vertex.x for vertex in box) * width),
            "y_max": int(max(vertex.y for vertex in box) * height)
        }
        localized_objects.append({"name": obj.name, "bounding_box": bounding_box})

    return localized_objects


def upload_to_gcs(image: BytesIO, file_name: str) -> str:
    """Uploads an image to Google Cloud Storage."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_file(image, content_type="image/png")
    blob.make_public()
    return blob.public_url


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# from flask import Flask, request, jsonify
# from io import BytesIO
# from PIL import Image
# import requests
# import datetime
# from rembg import remove
# from google.cloud import storage, vision
# from google.oauth2 import service_account
# import os

# app = Flask(__name__)

# # Please use your own service credentials
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
# storage_client = storage.Client()
# bucket_name = "os-api-assignment"

# credentials = service_account.Credentials.from_service_account_file("creds.json")
# vision_client = vision.ImageAnnotatorClient(credentials=credentials)


# @app.route("/remove-background", methods=["POST"])
# def remove_background():
#     try:
#         data = request.json
#         image_url = data.get("image_url")
#         use_vision_api = data.get("vision-api", "false").lower() == "true"

#         if not image_url:
#             return jsonify({"error": "Image URL is required"}), 400

#         # Fetch the image from the provided URL
#         response = requests.get(image_url)
#         if response.status_code != 200:
#             return jsonify({"error": "Unable to fetch image from URL"}), 400

#         image = Image.open(BytesIO(response.content)).convert("RGBA")

#         if use_vision_api:
#             localized_objects = detect_objects_vision_api(image_url)
#             object_urls = []
#             for idx, obj in enumerate(localized_objects):
#                 cropped_buffer = BytesIO()
#                 obj_image = image.crop(obj["bounding_box"])
#                 obj_image.save(cropped_buffer, format="PNG")
#                 cropped_buffer.seek(0)

#                 timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#                 file_name = f"object_{idx+1}_{obj['name']}_{timestamp}.png"

#                 object_url = upload_to_gcs(cropped_buffer, file_name)
#                 object_urls.append({"object_name": obj["name"], "url": object_url})

#             return jsonify({
#                 "message": "Objects processed with Vision API.",
#                 "objects": object_urls
#             }), 200
#         else:
#             # Default Rembg background removal
#             bounding_box = data.get("bounding_box", None)
#             if bounding_box is None:
#                 bounding_box = {"x_min": 0, "y_min": 0, "x_max": image.width, "y_max": image.height}

#             x_min = bounding_box["x_min"]
#             y_min = bounding_box["y_min"]
#             x_max = bounding_box["x_max"] if bounding_box["x_max"] else image.width
#             y_max = bounding_box["y_max"] if bounding_box["y_max"] else image.height

#             x_max = min(x_max, image.width)
#             y_max = min(y_max, image.height)
#             x_min = max(x_min, 0)
#             y_min = max(y_min, 0)

#             cropped_image = image.crop((x_min, y_min, x_max, y_max))
#             buffer = BytesIO()
#             processed_image = remove(cropped_image)
#             processed_image.save(buffer, format="PNG")
#             buffer.seek(0)

#             timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#             file_name = f"processed_image_{x_min}_{y_min}_{x_max}_{y_max}_{timestamp}.png"

#             processed_image_url = upload_to_gcs(buffer, file_name)

#             return jsonify({
#                 "original_image_url": image_url,
#                 "processed_image_url": processed_image_url
#             }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# def detect_objects_vision_api(image_url):
#     """Detects objects in the image using Google Vision API."""
#     response = requests.get(image_url)
#     content = response.content

#     image = vision.Image(content=content)
#     response = vision_client.object_localization(image=image)
#     objects = response.localized_object_annotations

#     localized_objects = []
#     for obj in objects:
#         box = obj.bounding_poly.normalized_vertices
#         bounding_box = (
#             int(box[0].x * 100),  
#             int(box[0].y * 100), 
#             int(box[2].x * 100),  
#             int(box[2].y * 100),  
#         )
#         localized_objects.append({"name": obj.name, "bounding_box": bounding_box})

#     return localized_objects


# def upload_to_gcs(image: BytesIO, file_name: str) -> str:
#     """Uploads an image to Google Cloud Storage."""
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(file_name)
#     blob.upload_from_file(image, content_type="image/png")
#     blob.make_public()
#     return blob.public_url


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8080))
#     app.run(host="0.0.0.0", port=port)




# from flask import Flask, request, jsonify
# from io import BytesIO
# from PIL import Image
# import requests
# import base64
# import datetime
# from rembg import remove
# from google.cloud import storage
# import os

# app = Flask(__name__)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "**"  # Replace with your service account
# storage_client = storage.Client()
# bucket_name = "os-api-assignment" 

# @app.route("/remove-background", methods=["POST"])
# def remove_background():
#     try:
#         data = request.json
#         image_url = data.get("image_url")
#         bounding_box = data.get("bounding_box", None)
        
#         if not image_url:
#             return jsonify({"error": "Image URL is required"}), 400
        
#         if bounding_box is None:
#             bounding_box = {"x_min": 0, "y_min": 0, "x_max": None, "y_max": None}

#         response = requests.get(image_url)
#         if response.status_code != 200:
#             return jsonify({"error": "Unable to fetch image from URL"}), 400
        
#         image = Image.open(BytesIO(response.content)).convert("RGBA")
        
#         x_min = bounding_box["x_min"]
#         y_min = bounding_box["y_min"]
#         x_max = bounding_box["x_max"] if bounding_box["x_max"] else image.width
#         y_max = bounding_box["y_max"] if bounding_box["y_max"] else image.height

#         x_max = min(x_max, image.width)
#         y_max = min(y_max, image.height)
#         x_min = max(x_min, 0)
#         y_min = max(y_min, 0)

#         cropped_image = image.crop((x_min, y_min, x_max, y_max))
#         buffer = BytesIO()
#         processed_image = remove(cropped_image) 
#         processed_image.save(buffer, format="PNG")
#         buffer.seek(0)
        
#         timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#         file_name = f"processed_image_{x_min}_{y_min}_{x_max}_{y_max}_{timestamp}.png"
        
#         processed_image_url = upload_to_gcs(buffer, file_name)
        
#         return jsonify({
#             "original_image_url": image_url,
#             "processed_image_url": processed_image_url
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# def upload_to_gcs(image: BytesIO, file_name: str) -> str:
#     """Uploads an image to Google Cloud Storage."""
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(file_name)
#     blob.upload_from_file(image, content_type="image/png")
#     blob.make_public()  
#     return blob.public_url


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8080))
#     app.run(host="0.0.0.0", port=port)



# GITHUB_TOKEN = "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"  # Personal access token
# GITHUB_REPO = "whysumedh/os-api"  # Format: username/repo_name
# GITHUB_BRANCH = "main"  


# def upload_to_github(image: BytesIO, file_name: str) -> str:
#     """Uploads an image to a GitHub repository."""
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
#     headers = {
#         "Authorization": f"Bearer {GITHUB_TOKEN}",
#         "Content-Type": "application/json"
#     }
    
#     # Convert the image to base64
#     image_base64 = base64.b64encode(image.getvalue()).decode("utf-8")
#     data = {
#         "message": f"Add {file_name}",
#         "content": image_base64,
#         "branch": GITHUB_BRANCH
#     }
    
#     response = requests.put(url, headers=headers, json=data)
#     if response.status_code in (200, 201):
#         return response.json()["content"]["download_url"]
#     else:
#         raise Exception(f"GitHub upload failed: {response.text}")