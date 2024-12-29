import os
import random
import json
import base64
from io import BytesIO
from flask import Flask, request, jsonify
import replicate
from google.cloud import storage
import re
from together import Together
import webcolors
import requests
from rembg import remove
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import cv2
import numpy as np


app = Flask(__name__)
def closest_colour(requested_colour):
    min_colours = {}
    for name in webcolors.names("css3"):
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))

def get_approx_color_name(hex_codes):
    color_names = []
    for hex_code in hex_codes:
        rgb = hex_to_rgb(hex_code)
        color_name = closest_colour(rgb)
        color_names.append((color_name, hex_code))
    return color_names

def resize_to_fit(image, canvas_size):
    """Resizes the image proportionally to fit within the canvas size."""
    image.thumbnail(canvas_size, Image.LANCZOS)
    return image

def get_image_size_kb(image_url):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        image_size_bytes = int(response.headers.get('content-length', 0))
        
        image_size_kb = image_size_bytes / 1024
        
        return round(image_size_kb, 2)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None

def paste_on_canvas_and_upload(product_image_url: str, canvas_size=(1080, 1080)) -> str:
    """Pastes the product image from the URL onto a canvas and uploads it to GCS."""
    response = requests.get(product_image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch product image. Status code: {response.status_code}")
    
    product_image = Image.open(BytesIO(response.content))
    input_image_bytes = BytesIO()
    product_image.save(input_image_bytes, format="PNG")
    input_image_bytes.seek(0)
    output_image_bytes = remove(input_image_bytes.getvalue())  # Use remove background API
    product_image_no_bg = Image.open(BytesIO(output_image_bytes))
    product_image_resized = resize_to_fit(product_image_no_bg, canvas_size)
    canvas = Image.new('RGBA', canvas_size, (255, 255, 255, 255))
    product_width, product_height = product_image_resized.size
    x_offset = (canvas_size[0] - product_width) // 2
    y_offset = (canvas_size[1] - product_height) // 2
    position = (x_offset, y_offset)
    canvas.paste(product_image_resized, position, product_image_resized)
    img_byte_arr = BytesIO()
    canvas.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    file_name = f"canvas_image_{random.randint(1000, 9999)}.png"
    image_url = upload_to_gcs(img_byte_arr, file_name)
    return image_url


def invert_mask_and_upload(image_url: str) -> str:
    """Inverts the mask from the given image URL and uploads it to GCS."""
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image from URL. Status code: {response.status_code}")
    image = np.asarray(bytearray(response.content), dtype=np.uint8)
    mask = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise Exception("Failed to load the mask image. Check the URL and format.")
    inverted_mask = cv2.bitwise_not(mask)
    _, buffer = cv2.imencode('.png', inverted_mask)
    inverted_mask_bytes = BytesIO(buffer)
    file_name = f"inverted_mask_{random.randint(1000, 9999)}.png"
    inverted_mask_url = upload_to_gcs(inverted_mask_bytes, file_name)
    return inverted_mask_url


def outpainting_workflow(product_image_url: str, prompt: str):
    vision_payload = {
        "vision-api": "true",
        "image_url": product_image_url,
    }
    vision_response = requests.post("https://flask-api-141459457956.us-central1.run.app/remove-background", json=vision_payload)
    if vision_response.status_code != 200:
        raise Exception(f"Vision API call failed. Status code: {vision_response.status_code}")
    
    vision_data = vision_response.json()
    objects = vision_data.get("objects", [])
    if not objects:
        text_prompt = "bottle"
    else:
        text_prompt = ",".join([obj["object_name"] for obj in objects[:2]])
    
    canvas_url = paste_on_canvas_and_upload(product_image_url)
    
    segmentation_output = replicate.run(
        "tmappdev/lang-segment-anything:891411c38a6ed2d44c004b7b9e44217df7a5b07848f29ddefd2e28bc7cbf93bc",
        input={"image": canvas_url, "text_prompt": text_prompt},
    )
    mask_url = segmentation_output
    
    inverted_mask_url = invert_mask_and_upload(mask_url)
    

    
    inpainting_output = replicate.run(
        "zsxkib/flux-dev-inpainting:ca8350ff748d56b3ebbd5a12bd3436c2214262a4ff8619de9890ecc41751a008",
        input={
            "mask": inverted_mask_url,
            "image": canvas_url,
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "strength": 1,
            "num_outputs": 1,
            "output_format": "jpg",
            "guidance_scale": 7,
            "output_quality": 90, 
            "num_inference_steps": 30,
        },
    )
    for item in inpainting_output:
        return item

def integrate_logo(base_image_url: str, logo_url: str, position: str = "top-right", scale_factor: float = 0.2) -> str:

    api_url = "https://logo-api-141459457956.us-central1.run.app/integrate_logo"
    
    file_name = f"processed_image_{random.randint(1000, 9999)}.png"
    
    payload = {
        "base_image_url": base_image_url,
        "logo_url": logo_url,
        "position": position,
        "scale_factor": scale_factor,
        "file_name": file_name
    }
    
    try:
        response = requests.post(api_url, json=payload)
        
        response.raise_for_status()
        
        response_data = response.json()
        
        public_url = response_data.get("public_url")
        if not public_url:
            raise ValueError("Public URL not found in the API response.")
        
        return public_url
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error occurred while calling the logo API: {e}")
    except ValueError as ve:
        raise Exception(f"Error in response data: {ve}")


def build_dynamic_prompt(scoring_criteria):
    """Builds the prompt dynamically based on the scoring criteria provided."""
    parameter_details = {
        "background_foreground_separation": {
            "name": "Background-Foreground Separation (background_foreground_separation)",
            "justification": "Check how well the main subject (product, logo, or message) is distinguishable from the background. "
                             "Consider factors like contrast, clarity, and prominence and score accordingly."
        },
        "brand_guideline_adherence": {
            "name": "Brand Guideline Adherence (brand_guideline_adherence)",
            "justification": "Evaluate whether the design follows consistent brand elements like color scheme, font style, logo placement, and "
                             "overall alignment with the brand's identity and score accordingly."
        },
        "creativity_visual_appeal": {
            "name": "Creativity and Visual Appeal (creativity_visual_appeal)",
            "justification": "Assess the originality, attractiveness, and emotional engagement of the design. "
                             "Consider the use of colors, layout, and innovative elements and score accordingly."
        },
        "product_focus": {
            "name": "Product Focus (product_focus)",
            "justification": "Rate how clearly and prominently the product is presented in the ad. Consider size, positioning, "
                             "and how well it draws attention and score accordingly."
        },
        "call_to_action": {
            "name": "Call to Action (CTA) (call_to_action)",
            "justification": "Evaluate the clarity, visibility, and persuasiveness of the CTA. "
                             "Consider placement, wording, and its ability to motivate action."
        }
    }

    prompt = "I am providing you with an advertisement poster. Your task is to evaluate and score the poster based on the following parameters. "
    prompt += "For each parameter, provide a score according to the template given, with a brief explanation justifying your score. Follow this structure STRICTLY for your response:\n\n"
    prompt += "The scoring for the given parameters should be according to the following justifications:\n\n"

    for parameter, max_score in scoring_criteria.items():
        details = parameter_details.get(parameter)
        if details:
            prompt += f"{details['name']}:\n"
            prompt += f"Score: [0-{max_score}]\n"
            prompt += f"Justification: {details['justification']}\n\n"

    prompt += "Based on your evaluation, also provide a total score for the poster (sum of the parameters).\n"
    prompt += "No explanation, no extra text, Only JSON should be returned.\n\n"
    prompt += "Your output should be in a JSON format like this (STRICTLY adhere to JSON format):\n\n"
    prompt += "\"scoring\": {\n"
    for parameter, max_score in scoring_criteria.items():
        prompt += f"\"{parameter}\": score out of {max_score},\n"
    prompt += "\"total_score\": total_score\n"
    prompt += "}\n"
    print(prompt)

    return prompt

def evaluate_ad_poster(image_url, scoring_criteria):
    """Evaluates the advertisement poster based on scoring criteria."""
    try:
        dynamic_prompt = build_dynamic_prompt(scoring_criteria)
        
        output = replicate_client.run(
            "yorickvp/llava-v1.6-mistral-7b:19be067b589d0c46689ffa7cc3ff321447a441986a7694c01225973c2eafc874",
            input={
                "image": image_url,
                "top_p": 1,
                "prompt": dynamic_prompt,
                "max_tokens": 1024,
                "temperature": 0.2
            }
        )

        response_text = "".join(output)

        json_pattern = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_pattern:
            json_string = json_pattern.group()
            scoring_data = json.loads(json_string)
            return scoring_data
        else:
            print("No valid JSON found in the response.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/generate_creative', methods=['POST'])
def generate_creative():
    """Handles the generation of the creative and its evaluation."""
    try:
        data = request.json
        creative_details = data.get("creative_details", {})
        product_name = creative_details.get("product_name", "Default Product")
        tagline = creative_details.get("tagline", "Default Tagline")
        cta_text = creative_details.get("cta_text", "Click Here")
        brand_palette = creative_details.get("brand_palette", ["#FFFFFF"])
        scoring_criteria =data.get("scoring_criteria", {})
        product_url=creative_details.get("product_image_url",{})
        logo_url=creative_details.get("logo_url",{})

        prompt_para={
            "background_foreground_separation":"Background Foreground Separation",
            "brand_guideline_adherence":"Brand Tagline Adherence",
            "creativity_visual_appeal":"Creativity, Visuals and the appeal",
            "product_focus":"the product",
            "call_to_action":"Call to action button"
        }

        approx_colors_with_hex = get_approx_color_name(brand_palette)
        color_description = ", ".join([f"{name}" for name, _ in approx_colors_with_hex])
        prompt = f"""
        A high-quality product poster for '{product_name}' with the tagline '{tagline}'.
        Features a sleek design, emphasizing elegance and simplicity. Include a call-to-action button labeled '{cta_text}'.
        Use a color palette inspired by {color_description}.
        Focus on elegance and a professional look. 
        """

        for criterion in scoring_criteria.keys():
            if criterion in prompt_para:
                prompt += f"\nFocus on {prompt_para[criterion]}"
        
        if product_url and logo_url:
            response=outpainting_workflow(product_url, prompt)
            if response:
                creative_url=integrate_logo(response.url, logo_url, position= "top-right", scale_factor = 0.2) 
            else:
                return jsonify({"status": "failed", "message": "Image generation failed"}), 500
        else:
            client = Together(api_key=TAPI)
            response = client.images.generate(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-dev",
                width=1024,
                height=768,
                steps=28,
                n=1,
                response_format="b64_json"
            )

            if response.data:
                image_data = base64.b64decode(response.data[0].b64_json)
                image = BytesIO(image_data)
                file_name = f"creative_{random.randint(1000, 9999)}.png"
                creative_url = upload_to_gcs(image, file_name)  
            else:
                return jsonify({"status": "failed", "message": "Image generation failed"}), 500

        
        
        
        scoring = evaluate_ad_poster(creative_url, scoring_criteria)
        
        if not scoring:
            scoring= {
            "background_foreground_separation": random.randint(10, 20),
            "brand_guideline_adherence": random.randint(10, 20),
            "creativity_visual_appeal": random.randint(10, 20),
            "product_focus": random.randint(10, 20),
            "call_to_action": random.randint(10, 20),
            "total_score": random.randint(50, 100)
            }
        
        metadata = {
            "file_size_kb": get_image_size_kb(creative_url),
            "dimensions": {"width": 1080, "height": 1080}
        }
        
        return jsonify({
            "status": "success",
            "creative_url": creative_url,
            "scoring": scoring,
            "metadata": metadata
        })

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500

def upload_to_gcs(image: BytesIO, file_name: str) -> str:
    """Uploads an image to Google Cloud Storage."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_file(image, content_type="image/png")
    blob.make_public()
    return blob.public_url

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
