import streamlit as st
import os
import replicate
import requests
from PIL import Image
from io import BytesIO
from google.cloud import storage
import random
import webcolors

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
os.environ["REPLICATE_API_TOKEN"] = st.secrets("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = "r8_MwO6YuoiwJFsDXpEB1IB0BIeGKSiPTG1P9qC5"
bucket_name = "os-api-assignment"
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

def upload_to_gcs(image: BytesIO, file_name: str) -> str:
    """Uploads an image to Google Cloud Storage and returns its public URL."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_file(image, content_type="image/png")
    blob.make_public()
    return blob.public_url

def download_image(url):
    """Downloads an image from a URL."""
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGBA")

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
    
    threshold = 200  
    logo_mask = logo_gray.point(lambda p: p > threshold and 255)  
    
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
        "top-left": (13, 13),
        "top-right": (base_image.width - logo.width - 10, 10),
        "bottom-left": (10, base_image.height - logo.height - 10),
        "bottom-right": (base_image.width - logo.width - 10, base_image.height - logo.height - 10)
    }
    if position not in positions:
        raise ValueError("Invalid position specified")
    base_image.paste(logo, positions[position], logo if "A" in logo.getbands() else None)
    return base_image

def integrate_logo_with_image(base_image_url, logo_url, brand_palette, position, scale_factor=0.2):
    base_image = download_image(base_image_url)
    logo = download_image(logo_url)
    logo = remove_background(logo)
    logo = resize_logo(logo, base_image, scale_factor)
    logo_recolored = recolor_logo(logo, base_image, brand_palette)
    final_image = paste_logo(base_image, logo_recolored, position)
    return final_image

st.set_page_config(page_title="AdCraft", page_icon=None)
st.title("AdCraft")
st.sidebar.image("adcraft.jpeg", use_container_width=True)
st.sidebar.header("Input Details")

product_name = st.text_input("Product Name", "GlowWell Skin Serum")
tagline = st.text_input("Tagline", "Radiance Redefined.")
cta_text = st.text_input("Call-to-Action Text", "Shop Now")

st.subheader("Brand Palette (Pick up to 5 colors)")
col1, col2, col3, col4, col5 = st.columns(5)

brand_palette = [
    col1.color_picker("Color 1", "#FFFFFF"),
    col2.color_picker("Color 2", "#FFFFFF"),
    col3.color_picker("Color 3", "#FFFFFF"),
    col4.color_picker("Color 4", "#FFFFFF"),
    col5.color_picker("Color 5", "#FFFFFF")
]
approx_colors_with_hex = get_approx_color_name(brand_palette)
color_description = ", ".join([f"{name}" for name, _ in approx_colors_with_hex])

logo_url = st.sidebar.text_input("Logo URL", "https://example.com/logo.png")
product_image_url = st.sidebar.text_input("Product Image URL", "https://example.com/product.png")

aspect_ratio = st.sidebar.selectbox(
    "Select Aspect Ratio",
    ["1:1", "16:9", "21:9", "3:2", "2:3", "4:5", "5:4", "3:4", "4:3", "9:16", "9:21"]
)

aspect_ratio_dict = {
    "1:1": (1, 1),
    "16:9": (16, 9),
    "21:9": (21, 9),
    "3:2": (3, 2),
    "2:3": (2, 3),
    "4:5": (4, 5),
    "5:4": (5, 4),
    "3:4": (3, 4),
    "4:3": (4, 3),
    "9:16": (9, 16),
    "9:21": (9, 21),
}

width, height = aspect_ratio_dict[aspect_ratio]


if "images" not in st.session_state:
    st.session_state.images = []
if "selected_image_idx" not in st.session_state:
    st.session_state.selected_image_idx = None

if st.sidebar.button("Generate Poster"):
    with st.spinner("Generating Images..."):
        try:
            prompt = (
                f"A high-quality product advertisement for '{product_name}' with the tagline '{tagline}'. "
                f"Features a sleek design, emphasizing elegance and simplicity. Include a call-to-action button labeled '{cta_text}'. "
                f"Use a color palette inspired by {color_description}. Focus on elegance and a professional look."
            )

            output = replicate_client.run(
                "black-forest-labs/flux-dev",
                input={
                    "prompt": prompt,
                    "aspect_ratio": f"{width}:{height}",
                    "num_outputs": 3,
                    "num_inference_steps": 28,
                },
            )

            st.session_state.images = [download_image(img.url) for img in output]
            st.session_state.selected_image_idx = None
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

if st.session_state.images:
    st.subheader("Generated Posters")
    for idx, img in enumerate(st.session_state.images):
        st.image(img, caption=f"Image {idx + 1}", use_container_width=True)

    st.session_state.selected_image_idx = st.radio(
        "Select an image",
        options=range(len(st.session_state.images)),
        format_func=lambda x: f"Image {x + 1}",
        index=st.session_state.selected_image_idx or 0,
    )

    if st.session_state.selected_image_idx is not None:
        selected_image = st.session_state.images[st.session_state.selected_image_idx]

        if st.button("Liked this Image? Now Integrate your Product"):
                buffer = BytesIO()
                selected_image.save(buffer, format="PNG")
                buffer.seek(0)
                file_name = f"creative_{random.randint(1000, 9999)}.png"
                creative_url = upload_to_gcs(buffer, file_name)
                st.success(f"Image uploaded successfully: {creative_url}")

                payload = {"vision-api": "true", "image_url": creative_url}
                response = requests.post(
                    "https://flask-api-141459457956.us-central1.run.app/remove-background",
                    json=payload,
                )

                if response.status_code == 200:
                    objects = response.json().get("objects", [])
                    object_names = [obj["object_name"] for obj in objects]
                    if not object_names:
                        selected_objects = ["Bottle"]
                    else:
                        selected_objects = sorted(object_names, key=lambda x: len(x.split()))[:2]
                    
                    st.write(f"Selected Objects: {', '.join(selected_objects)}")
                    st.write(f"Mask Input - Image: {creative_url}, Prompt: {','.join(selected_objects)}")


                    mask_output = replicate_client.run(
                        "tmappdev/lang-segment-anything:891411c38a6ed2d44c004b7b9e44217df7a5b07848f29ddefd2e28bc7cbf93bc",
                        input={"image": creative_url, "text_prompt": ",".join(selected_objects)},
                    )


                    if mask_output:
                        mask_url = mask_output
                        response = requests.get(mask_url)
                        response.raise_for_status()
                        mask_image = Image.open(BytesIO(response.content))
                        st.image(mask_image, caption="Masked Image")

                        product_description_output = replicate_client.run(
                            "zsxkib/molmo-7b:76ebd700864218a4ca97ac1ccff068be7222272859f9ea2ae1dd4ac073fa8de8",
                            input={
                                "image": product_image_url,
                                "text": "Describe this image for regeneration, include keywords, should be concise, only the description of the product NO CREATIVE LIBERTY",               
                                "top_k": 50,
                                "top_p": 1,
                                "temperature": 1,
                                "length_penalty": 0.8,
                                "max_new_tokens": 896

                            },
                        )


                        st.write("Product Description:", product_description_output)

                        mask_url=str(mask_url)
                        if isinstance(mask_url, str) and isinstance(creative_url, str):

                            inpainting_output = replicate_client.run(
                                "andreasjansson/stable-diffusion-inpainting:e490d072a34a94a11e9711ed5a6ba621c3fab884eda1665d9d3a282d65a21180",
                                input={
                                    "mask": mask_url,
                                    "image": creative_url,
                                    "prompt": product_description_output,
                                    "invert_mask": False,
                                    "guidance_scale": 7.5,
                                    "negative_prompt": "",
                                    "num_inference_steps": 50
                                },
                            )
                        else:
                            st.error("Error: Invalid URL provided for mask or creative image.")

                        if isinstance(inpainting_output, list) and len(inpainting_output) > 0 and hasattr(inpainting_output[0], "url"):
                            inpainting_url = inpainting_output[0].url
                            response = requests.get(inpainting_url)
                            response.raise_for_status()
                            inpainted_image = Image.open(BytesIO(response.content))

                            st.image(inpainted_image, caption="Final Image with Inpainting")
                            buffer = BytesIO()
                            inpainted_image.save(buffer, format="PNG")
                            buffer.seek(0)
                            file_name = f"inpainted_image_{random.randint(1000, 9999)}.png"  
                            inpainted_image_url = upload_to_gcs(buffer, file_name)
                            
                            st.success(f"Inpainted image uploaded successfully: {inpainted_image_url}")
                            if inpainted_image_url:
                                st.write("Integrating logo with the inpainted image...")
                                position = st.radio(
                                "Select Logo Position",
                                options=["top-right", "top-left", "bottom-left", "bottom-right"],
                                index=0,
                                )
                                logo_integration_payload = {
                                    "base_image_url": inpainted_image_url,
                                    "logo_url": logo_url,
                                    "brand_palette": brand_palette,
                                    "position": position, 
                                    "scale_factor": 0.2,
                                    "file_name": f"final_{random.randint(1000, 9999)}.png"
                                }
                                try:
                                    response = requests.post("https://logo-integration-api-141459457956.us-central1.run.app/integrate_logo", json=logo_integration_payload)
                                    response.raise_for_status()
                                    logo_integration_result = response.json()

                                    if "public_url" in logo_integration_result:
                                        final_poster_url = logo_integration_result["public_url"]
                                        st.image(final_poster_url, caption="Final Advertisement Poster with Logo")
                                        st.success(f"Final poster uploaded successfully: {final_poster_url}")
                                    else:
                                        st.error("Error: No URL found in the logo API response.")
                                except Exception as e:
                                    st.error(f"Error during logo integration: {str(e)}")
                        else:
                            st.error("Error in generating inpainted image")
                    else:
                        st.error("Error in generating masked image")
                else:
                    st.error("Error in processing background removal")

