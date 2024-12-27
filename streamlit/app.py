import streamlit as st
import os
import io
import replicate
import requests
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from io import BytesIO
from google.cloud import storage
import random
import webcolors
import base64
from together import Together

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
os.environ["REPLICATE_API_TOKEN"] = st.secrets("REPLICATE_API_TOKEN")
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

def edit_poster(image, contrast, brightness, sharpness, price, font_size, x_offset, y_offset, box_color, text_color, box_opacity, box_shape, corner_radius):
    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    if sharpness != 1.0:
        image = ImageEnhance.Sharpness(image).enhance(sharpness)

    if price:
        draw = ImageDraw.Draw(image, "RGBA")
        font = ImageFont.truetype("arial.ttf", font_size)  
        
        text_width = draw.textlength(price, font=font)
        text_height = font.size
        padding = 10
        box_width = text_width + 2 * padding
        box_height = text_height + 2 * padding

        box_xy = (x_offset, y_offset, x_offset + box_width, y_offset + box_height)
        text_xy = (x_offset + padding, y_offset + padding)

        rgba_box_color = (*tuple(int(box_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)), int(box_opacity * 255))

        if box_shape == "Rectangle":
            draw.rectangle(box_xy, fill=rgba_box_color)
        elif box_shape == "Rounded Rectangle":
            draw.rounded_rectangle(box_xy, radius=corner_radius, fill=rgba_box_color)
        elif box_shape == "Ellipse":
            draw.ellipse(box_xy, fill=rgba_box_color)
        
        draw.text(text_xy, price, fill=text_color, font=font)

    return image

def send_request_to_together(prompt, model, image_url):
    client = Together(api_key=TAPI)

    response = client.images.generate(
        model=model,
        width=1024,
        height=768,
        steps=28,
        prompt=prompt,
        image_url=image_url
    )
    return response

st.set_page_config( page_title="AdCraft", page_icon="favicon_adcraft.jpg",layout="wide")
st.title("AdCraft")
tab1, tab2, tab3=st.tabs(["Creative Generation", "Edit Creative", "Modify the Creative with AI"])

with tab1:
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

    logo_url = st.sidebar.text_input("Logo URL*", "https://i.pinimg.com/originals/3d/36/c4/3d36c4b13e125ae1bbb4f818ab2c3e80.jpg")
    product_image_url = st.sidebar.text_input("Product Image URL*", "https://erbaturglass.com/asset/resized/urunler/serumbottle/50ml/w_50ml3_m.jpg")

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
    st.sidebar.write("*Note:* Please Include both Logo and Image URLs ")
    st.sidebar.write("*Note:* Default URLs are set to Loreal Logo and Generic Face Serum Product Image ")
    st.sidebar.write("Made to win by Team RAG2riches")
    

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
        num_images = len(st.session_state.images)
        cols = st.columns(num_images)
        for idx, img in enumerate(st.session_state.images):
            with cols[idx]:
                st.image(img, caption=f"Image {idx + 1}", width=500)

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
                    st.write("Detecting objects...")

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
                        st.write("Masking the image...")


                        mask_output = replicate_client.run(
                            "tmappdev/lang-segment-anything:891411c38a6ed2d44c004b7b9e44217df7a5b07848f29ddefd2e28bc7cbf93bc",
                            input={"image": creative_url, "text_prompt": ",".join(selected_objects)},
                        )

                        
                        if mask_output:
                            mask_url = mask_output
                            response = requests.get(mask_url)
                            response.raise_for_status()
                            mask_image = Image.open(BytesIO(response.content))
                            st.image(mask_image, caption="Masked Image", width=600)
                            st.write("Generating Product Description for the given Product image URL")
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
                            st.write("Inpainting the product....")

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
                                st.session_state["logo_url"] = inpainted_image_url
                                if "logo_url" in st.session_state:
                                    st.write("Integrating logo with the inpainted image...")
                                    position = st.radio(
                                    "Select Logo Position",
                                    options=["top-right", "top-left", "bottom-left", "bottom-right"]
                                    )
                                    logo_integration_payload = {
                                        "base_image_url": st.session_state["logo_url"],
                                        "logo_url": logo_url,
                                        "brand_palette": brand_palette,
                                        "position": position, 
                                        "scale_factor": 0.2,
                                        "file_name": f"final_{random.randint(1000, 9999)}.png"
                                    }
                                    if position:
                                        try:
                                            response = requests.post("https://logo-api-141459457956.us-central1.run.app/integrate_logo", json=logo_integration_payload)
                                            response.raise_for_status()
                                            logo_integration_result = response.json()

                                            if "public_url" in logo_integration_result:
                                                final_poster_url = logo_integration_result["public_url"]
                                                st.image(final_poster_url, caption="Final Advertisement Poster with Logo")
                                                st.success(f"Final poster uploaded successfully: {final_poster_url}")
                                                st.session_state["final_url"] = final_poster_url
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


with tab2:
    st.header("Creative Editor")
    uploaded_file = st.file_uploader("Upload an Creative", type=["jpg", "jpeg", "png"])
    image_url = st.text_input("Or, provide an image URL")
    if "final_url" in st.session_state:
        image_url=st.session_state["final_url"]

    image = None  

    if image_url:
        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            st.success("Image loaded from URL successfully!")
        except Exception as e:
            st.error(f"Failed to load image from URL: {e}")
    elif uploaded_file:
        image = Image.open(uploaded_file)

    if image:
        col1, col2 = st.columns([2, 1])

        with col2:
            st.header("Edit Parameters")
            col1_param, col2_param = st.columns(2)

            with col1_param:
                contrast = st.slider("Contrast", 0.5, 2.0, 1.0, step=0.1)
                brightness = st.slider("Brightness", 0.5, 2.0, 1.0, step=0.1)
                sharpness = st.slider("Sharpness", 0.5, 2.0, 1.0, step=0.1)

            with col2_param:
                price = st.text_input("Price (e.g., Rs 299)", "")
                font_size = st.slider("Font Size", 10, 100, 20)
                x_offset = st.slider("X Offset", 0, image.width, 0)
                y_offset = st.slider("Y Offset", 0, image.height, 0)

            box_color = st.color_picker("Box Color", "#FFFF00")
            text_color = st.color_picker("Text Color", "#000000")
            box_opacity = st.slider("Box Opacity", 0.0, 1.0, 1.0, step=0.1)
            box_shape = st.selectbox("Box Shape", ["Rectangle", "Rounded Rectangle", "Ellipse"])

            corner_radius = 0
            if box_shape == "Rounded Rectangle":
                corner_radius = st.slider("Corner Radius", 0, 50, 10)

        edited_image = edit_poster(image.copy(), contrast, brightness, sharpness, price, font_size, x_offset, y_offset, box_color, text_color, box_opacity, box_shape, corner_radius)

        with col1:
            st.image(edited_image, caption="Edited Poster", use_container_width=True)

            img_byte_arr = io.BytesIO()
            edited_image.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)
            st.download_button(
                label="Download Edited Image",
                data=img_byte_arr,
                file_name="edited_poster.png",
                mime="image/png"
            )

with tab3:
    if "final_url" in st.session_state and st.session_state["final_url"]:
        image_url = st.session_state["final_url"]

        st.image(image_url, caption="Uploaded Image")

        action = st.selectbox("Choose Action", ["Enhance the Image", "Modify the Image"])
        prompt = "."
        if action == "Modify the Image":
            prompt = st.text_input("Enter modification prompt", "e.g., Add a surreal vibe")

        if st.button("Submit"):
            try:
                model = "black-forest-labs/FLUX.1-redux" if action == "Enhance the Image" else "black-forest-labs/FLUX.1-canny"
                result = send_request_to_together(
                    prompt=prompt,
                    model=model,
                    image_url=image_url
                )

                modified_image_url = result.data[0].url

                st.image(modified_image_url, caption="Modified Image", use_container_width=True)

                st.download_button(
                    label="Download Modified Image",
                    data=modified_image_url,
                    file_name="modified_image.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("No image URL found in session state. Please upload an image in the previous tab.")

                    st.error("Error in processing background removal")

