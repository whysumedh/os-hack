import streamlit as st
import os
import io
import replicate
import requests
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from google.cloud import storage
import random
import webcolors
from together import Together
from rembg import remove
from serpapi import GoogleSearch
from opencage.geocoder import OpenCageGeocode
from streamlit_folium import st_folium
import folium
from datetime import datetime
import plotly.graph_objects as go

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "JSONFILE"
TAPI="**"
bucket_name = "os-api-assignment"
OPENCAGE_API_KEY = "**"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

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

def fetch_trends_data(query, date_range):
    params = {
        "engine": "google_trends",
        "q": query, 
        "data_type": "TIMESERIES", 
        "date": date_range, 
        "api_key": "f3c99f2475d6e0b915a0eeda1b9e917436016b1c4048fb6167dce80a863a7b02"  
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("interest_over_time", {}).get("timeline_data", [])

def process_timeseries_data(timeseries_data):
    query_data = {}
    for entry in timeseries_data:
        for value in entry['values']:
            query = value['query']
            extracted_value = value['extracted_value']
            timestamp = entry['timestamp']

            if query not in query_data:
                query_data[query] = {"timestamps": [], "values": []}
            query_data[query]["timestamps"].append(int(timestamp))
            query_data[query]["values"].append(int(extracted_value))
    return query_data

def fetch_regional_data(query):
    params = {
        "engine": "google_trends",
        "q": query,
        "geo": "IN",
        "region": "REGION",
        "data_type": "GEO_MAP_0",
        "api_key": "f3c99f2475d6e0b915a0eeda1b9e917436016b1c4048fb6167dce80a863a7b02",
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("interest_by_region", [])

def trends_fetcher(query):
    day_data = fetch_trends_data(query, "now 1-d")
    week_data = fetch_trends_data(query, "now 7-d")
    regional_data = fetch_regional_data(query)

    if day_data and week_data:
        day_query_data = process_timeseries_data(day_data)

        week_query_data = process_timeseries_data(week_data)

        best_times = []
        for query, data in day_query_data.items():
            timestamps = data["timestamps"]
            values = data["values"]
            readable_times = [datetime.fromtimestamp(ts) for ts in timestamps]

            peak_value = max(values)
            peak_index = values.index(peak_value)
            peak_time = readable_times[peak_index]
            best_times.append((query, peak_value, peak_time))

        best_days = []
        for query, data in week_query_data.items():
            timestamps = data["timestamps"]
            values = data["values"]
            readable_times = [datetime.fromtimestamp(ts) for ts in timestamps]

            peak_value = max(values)
            peak_index = values.index(peak_value)
            peak_time = readable_times[peak_index]
            peak_day = peak_time.strftime('%A')
            best_days.append((query, peak_value, peak_day))

        st.subheader("Best Time to Post the Ad")
        for i, query in enumerate(day_query_data.keys()):
            best_time_of_day = best_times[i][2].strftime('%I:%M %p')  # Format time
            best_value_of_day = best_times[i][1]
            best_day_of_week = best_days[i][2]
            best_value_of_week = best_days[i][1]

            st.write(f"**Query: {query}**")
            st.write(f"- Best Time of Day: {best_time_of_day} (Peak Value: {best_value_of_day})")
            st.write(f"- Best Day of the Week: {best_day_of_week} (Peak Value: {best_value_of_week})")

        fig_day = go.Figure()
        for query, data in day_query_data.items():
            timestamps = data["timestamps"]
            values = data["values"]
            readable_times = [datetime.fromtimestamp(ts) for ts in timestamps]

            fig_day.add_trace(go.Scatter(
                x=readable_times,
                y=values,
                mode='lines+markers',
                name=query
            ))
        fig_day.update_layout(
            title="Interest Over Time (Past Day)",
            xaxis_title="Time",
            yaxis_title="Interest Value",
            legend_title="Queries",
            template="plotly_white",
            hovermode="x unified"
        )

        fig_week = go.Figure()
        for query, data in week_query_data.items():
            timestamps = data["timestamps"]
            values = data["values"]
            readable_times = [datetime.fromtimestamp(ts) for ts in timestamps]

            fig_week.add_trace(go.Scatter(
                x=readable_times,
                y=values,
                mode='lines+markers',
                name=query
            ))
        fig_week.update_layout(
            title="Interest Over Time (Past Week)",
            xaxis_title="Time",
            yaxis_title="Interest Value",
            legend_title="Queries",
            template="plotly_white",
            hovermode="x unified"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Past Day Trends")
            st.plotly_chart(fig_day, use_container_width=True)

        with col2:
            st.subheader("Past Week Trends")
            st.plotly_chart(fig_week, use_container_width=True)

    if regional_data:
        st.subheader("Top 5 Regions")
        regions = sorted(regional_data, key=lambda x: x["extracted_value"], reverse=True)[:5]

        m = folium.Map(location=[23.5937, 80.9629], zoom_start=5, tiles="cartodbpositron")

        for region in regions:
            location_name = region["location"]
            value = region["extracted_value"]

            geo_data = geocoder.geocode(location_name + ", India")
            if geo_data:
                lat, lng = geo_data[0]["geometry"]["lat"], geo_data[0]["geometry"]["lng"]

                folium.Marker(
                    location=[lat, lng],
                    tooltip=f"{location_name}: {value}",
                    icon=folium.Icon(color="blue"),
                ).add_to(m)

        st_folium(m, width=800, height=600)
    else:
        st.warning("No regional data found for the selected query.")


def edit_poster(image, contrast, brightness, sharpness, price, font_size, x_offset, y_offset, box_color, text_color, box_opacity, box_shape, corner_radius):
    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    if sharpness != 1.0:
        image = ImageEnhance.Sharpness(image).enhance(sharpness)

    if price:
        draw = ImageDraw.Draw(image, "RGBA")
        font = ImageFont.truetype("Arial.ttf", font_size)  
        
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

def resize_to_fit(image, canvas_size):
    """Resizes the image proportionally to fit within the canvas size."""
    image.thumbnail(canvas_size, Image.LANCZOS)
    return image

def paste_on_canvas_and_upload(product_image_url: str, canvas_size=(1080, 1080)) -> str:
    """Pastes the product image from the URL onto a canvas and uploads it to GCS."""
    
    response = requests.get(product_image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch product image. Status code: {response.status_code}")
    
    product_image = Image.open(BytesIO(response.content))
    
    input_image_bytes = BytesIO()
    product_image.save(input_image_bytes, format="PNG")
    input_image_bytes.seek(0)
    output_image_bytes = remove(input_image_bytes.getvalue())
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
    """
    Inverts the mask from the given image URL and uploads it to GCS.
    """
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image from URL. Status code: {response.status_code}")
    
    try:
        image = Image.open(BytesIO(response.content)).convert('L')
    except Exception as e:
        raise Exception(f"Failed to load the mask image. Error: {e}")
    
    inverted_mask = ImageOps.invert(image)
    
    buffer = BytesIO()
    inverted_mask.save(buffer, format='PNG')
    buffer.seek(0) 
    
    file_name = f"inverted_mask_{random.randint(1000, 9999)}.png"
    
    inverted_mask_url = upload_to_gcs(buffer, file_name)
    
    return inverted_mask_url


def outpainting_workflow(product_image_url: str, product_name: str, tagline: str, cta_text: str, color_description: str):
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
    st.image(canvas_url,caption="Product Pasted on Canvas",width=800)
    segmentation_output = replicate.run(
        "tmappdev/lang-segment-anything:891411c38a6ed2d44c004b7b9e44217df7a5b07848f29ddefd2e28bc7cbf93bc",
        input={"image": canvas_url, "text_prompt": text_prompt},
    )
    mask_url = segmentation_output
    
    inverted_mask_url = invert_mask_and_upload(mask_url)
    st.image(inverted_mask_url,caption="Inverted Mask for Outpainting",width=800)

    
    prompt = (
        f"A high-quality product advertisement for '{product_name}' with the tagline '{tagline}'. "
        f"Features a sleek design, emphasizing elegance and simplicity. Include a call-to-action button labeled '{cta_text}'. "
        f"Use a color palette inspired by {color_description}. Focus on elegance and a professional look."
    )
    
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

st.set_page_config( page_title="AdCraft", page_icon="favfav.jpg",layout="wide")
st.title("AdCraft")
tab1, tab2, tab3, tab4, tab5=st.tabs(["Inpainter 🖼️🖌️","Outpainter 🎨🖌️","Google Trends", "Edit Creative", "Modify the Creative with AI"])

st.sidebar.image("adcraft.jpeg", use_container_width=True)
st.sidebar.header("Input Details")
logo_url = st.sidebar.text_input("Logo URL*", "https://images.seeklogo.com/logo-png/35/1/nykaa-logo-png_seeklogo-358073.png?v=1957301131966779968")
st.session_state["logo_url_op"]=logo_url
product_image_url = st.sidebar.text_input("Product Image URL*", "https://erbaturglass.com/asset/resized/urunler/serumbottle/50ml/w_50ml3_m.jpg")
repapi=st.sidebar.text_input("Provide your Replicate API Token")
os.environ["REPLICATE_API_TOKEN"] = repapi
st.session_state["product_url_op"]=product_image_url
st.sidebar.write("*Note:* Please Include both Logo and Image URLs ")
st.sidebar.write("*Note:* Default URLs are set to Nykaa Logo and Generic Face Serum Product Image ")
st.sidebar.write("*Inpainting* - Descripts the given product image and regenerates the product from the user chosen poster ")
st.sidebar.write("*Outpainting* - Keeps the product image intact and generates background with the given prompt ")
endpoint="https://creative-api-141459457956.us-central1.run.app/generate_creative"
st.sidebar.write("To use this as API, use this [endpoint](%s)"%endpoint)
interface="https://os-hack.vercel.app/"
st.sidebar.write("Or use the API interface [here](%s)"%interface)
doc="https://github.com/whysumedh/os-hack/blob/main/README.md"
st.sidebar.write("Check the documentation [here](%s)"%doc)
st.sidebar.write("Made to Win by Team RAG2riches")


with tab1:

    product_name = st.text_input("Product Name", "GlowWell Skin Serum")
    words_ip = product_name.split()
    query_ip = " ".join(words_ip[1:]) 
    tagline = st.text_input("Tagline", "Radiance Redefined.")
    cta_text = st.text_input("Call-to-Action Text", "Shop Now")
    aspect_ratio = st.selectbox(
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

    if aspect_ratio:
        width, height = aspect_ratio_dict[aspect_ratio]

    st.write("Brand Palette")
    col1, col2, col3, col4, col5 = st.columns(5)

    brand_palette = [
        col1.color_picker("Color 1", "#FFFFFF"),
        col2.color_picker("Color 2", "#FFFFFF"),
        col3.color_picker("Color 3", "#FFFFFF"),
    ]
    approx_colors_with_hex = get_approx_color_name(brand_palette)
    color_description = ", ".join([f"{name}" for name, _ in approx_colors_with_hex])
    logo_position = st.radio("Select Logo Position",options=["top-right", "top-left", "bottom-left", "bottom-right"])

    if "images" not in st.session_state:
        st.session_state.images = []
    if "selected_image_idx" not in st.session_state:
        st.session_state.selected_image_idx = None

    if st.button("Generate"):
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

                                st.image(inpainted_image, caption="Final Image with Inpainting", width=800)
                                buffer = BytesIO()
                                inpainted_image.save(buffer, format="PNG")
                                buffer.seek(0)
                                file_name = f"inpainted_image_{random.randint(1000, 9999)}.png"  
                                inpainted_image_url = upload_to_gcs(buffer, file_name)
                                
                                st.success(f"Inpainted image uploaded successfully: {inpainted_image_url}")
                                st.session_state["logo_url"] = inpainted_image_url
                                if "logo_url" in st.session_state:
                                    st.write("Integrating logo with the inpainted image...")
                                    logo_integration_payload = {
                                        "base_image_url": st.session_state["logo_url"],
                                        "logo_url": logo_url,
                                        "brand_palette": brand_palette,
                                        "position": logo_position, 
                                        "scale_factor": 0.3,
                                        "file_name": f"final_{random.randint(1000, 9999)}.png"
                                    }
                                    try:
                                        response = requests.post("https://logo-api-141459457956.us-central1.run.app/integrate_logo", json=logo_integration_payload)
                                        response.raise_for_status()
                                        logo_integration_result = response.json()

                                        if "public_url" in logo_integration_result:
                                            final_poster_url = logo_integration_result["public_url"]
                                            st.image(final_poster_url, caption="Final Ad Creative with Logo", width = 800)
                                            st.success(f"Final poster uploaded successfully: {final_poster_url}")
                                            st.session_state["final_url"] = final_poster_url
                                        else:
                                            st.error("Error: No URL found in the logo API response.")
                                    except Exception as e:
                                        st.error(f"Error during logo integration: {str(e)}")
                                    st.session_state["qipa"] = query_ip
                            else:
                                st.error("Error in generating inpainted image")
                        else:
                            st.error("Error in generating masked image")
                    else:
                        st.error("Error in processing background removal")


with tab2:

    product_name_op = st.text_input("Name of the Product", "GlowWell Skin Serum")
    words_op = product_name.split()
    query_op = " ".join(words_op[1:]) 
    tagline_op = st.text_input("Product Tagline", "Radiance Redefined.")
    cta_text_op = st.text_input("Call to Action Text", "Shop Now")
    col1,col2=st.columns(2)
    with col1:
        height=st.number_input("Height",1024)
    with col2:
        width=st.number_input("Width",1024)

    

    st.subheader("Choose Brand Palette")
    col1, col2, col3, col4, col5 = st.columns(5)

    brand_palette_op = [
        col1.color_picker("Colour 1", "#FFFFFF"),
        col2.color_picker("Colour 2", "#FFFFFF"),
        col3.color_picker("Colour 3", "#FFFFFF")
    ]
    approx_colors_with_hex_op = get_approx_color_name(brand_palette_op)
    color_description_op = ", ".join([f"{name}" for name, _ in approx_colors_with_hex_op])
    st.write(color_description_op)
    logo_position_op = st.radio("Choose Logo Position",options=["top-right", "top-left", "bottom-left", "bottom-right"])
    if "logo_url_op" in st.session_state:
        logo_url_op=st.session_state["logo_url_op"]
    if "product_url_op" in st.session_state:
        product_url_op=st.session_state["product_url_op"]
    
    if st.button("Generate Creative"):
        response_op = outpainting_workflow( product_url_op, product_name_op, tagline_op, cta_text_op, color_description_op )
        st.image(response_op.url,caption="Outpainted Poster with Intact Product Image",width=800)
        final_logo_url= integrate_logo(response_op.url, logo_url_op, logo_position_op, scale_factor = 0.2)
        st.image(final_logo_url, caption="Final Creative With Logo", width=800)
        st.session_state["final_url"] = final_logo_url
        st.session_state["qopa"]=query_op


with tab3:
    if "qipa" in st.session_state and st.session_state["qipa"]:
        q=st.session_state["qipa"]
        trends_fetcher(q)
    
    if "qopa" in st.session_state and st.session_state["qopa"]:
        q=st.session_state["qopa"]
        trends_fetcher(q)
    else:
        st.warning("No creative is generated in the session. Generate a creative to check trends")


with tab4:
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

with tab5:
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

                st.image(modified_image_url, caption="Modified Image", width=800)

                st.download_button(
                    label="Download Modified Image",
                    data=modified_image_url,
                    file_name="modified_image.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("No image URL found in session. Please generate a creative for the modifications.")
