# **AdCraft : Your Ads, Your Way, All Day!**

This project enables users to generate customized Ad creatives by leveraging an API for creative generation, Google Cloud Storage for storing generated images, and multiple models. It automates the process of generating ad creatives by combining uploaded images, masks, and logos seamlessly.


---
![adcraft](https://github.com/user-attachments/assets/f22c192e-92f8-44cf-a2d1-2213b943f79f)

---

## Table of Contents
1. [Demo Video](#demo-video)
2. [Hosted Apps](#hosted-apps)
3. [Hosted APIs](#hosted-apis)
4. [Workflow and Architecture](#workflow-and-architecture)
5. [Hosted APIs Payload and Response](#hosted-apis-payload-and-response)
6. [Features](#features)
7. [Technologies Used](#technologies-used)
8. [Installation and Setup](#installation-and-setup)

## 🔗 Demo Video
- Sped up the video to 1.5x
https://drive.google.com/drive/folders/1A1vtRV-iDrYIjKYmGxwpRpCNWGjBOHEt

## 🔗 Hosted Apps

- Check out the react API Interface we have created for this app: https://os-hack.vercel.app/ .(Please Make sure CORS policy is turned off before use) 
- Check out the Streamit App we have created for customizable image generation: https://adcraft.streamlit.app/

## 🔗 Hosted APIs

All the API Codes have been uploaded to the repo with their respective folder names.

- Creative Generation API - https://creative-api-141459457956.us-central1.run.app/generate_creative - For creative generation and scoring of the creative according to the payload given.
- Cloud Vision API - https://flask-api-141459457956.us-central1.run.app/remove-background - To use cloud vision API for object detection for masking of images
- Logo Integration API - https://logo-api-141459457956.us-central1.run.app/integrate_logo - Uses Pillow and other libraries to inteagrate logo with a base image according to user preference.
- We used several hosted models in [replicate.com](https://replicate.com/) and [together.ai](https://www.together.ai/) as APIs

## Workflow and Architecture

### Streamlit Interface
![OS-HACK (2)](https://github.com/user-attachments/assets/d0a3537f-bfee-4d0e-aeef-5eff07c44aa9)

### Creative Generation API
![api-workflow](https://github.com/user-attachments/assets/afac8adc-7966-4d34-9887-2296135174b7)

### For Optimized Product Regeneration
As discussed in the demo video, this is how an optimized product regeneration would be possible, (due to time and computational constraints we could not implement this and trying to update the below workflow model) essentially the inpainting will be done with an image prompt (instead of text description of the product image):
![image](https://github.com/user-attachments/assets/3e69b48f-3427-479b-823b-e26fbcaacfc5)


## 🔗 Hosted APIs Payload and Response

Creative Generation API - https://creative-api-141459457956.us-central1.run.app/generate_creative - For creative generation and scoring of the creative according to the payload given.
### Payload
```
{
    "creative_details": {
        "product_name": "GlowWell Skin Serum",
        "tagline": "Radiance Redefined.",
        "brand_palette": [
            "#FFC107",
            "#212121",
            "#FFFFFF"
        ],
        "dimensions": {
            "width": 1080,
            "height": 1080
        },
        "cta_text": "Shop Now",
        "logo_url": "https://images.seeklogo.com/logo-png/35/1/nykaa-logo-png_seeklogo-358073.png?v=1957301131966779968",
        "product_image_url": "https://erbaturglass.com/asset/resized/urunler/serumbottle/50ml/w_50ml3_m.jpg"
    },
    "scoring_criteria": {
        "background_foreground_separation": 50,
        "brand_guideline_adherence": 50
    }
}
```
### Response
```
{
    "creative_url": "https://storage.googleapis.com/os-api-assignment/processed_image_5911.png",
    "metadata": {
        "dimensions": {
            "height": 1080,
            "width": 1080
        },
        "file_size_kb": 441.42
    },
    "scoring": {
        "scoring": {
            "background_foreground_separation": 40,
            "brand_guideline_adherence": 45,
            "total_score": 85
        }
    },
    "status": "success"
}
```
Cloud Vision API - https://flask-api-141459457956.us-central1.run.app/remove-background - To use cloud vision API for object detection for masking of images
### Payload
```
{
    "vision-api":"true",
    "image_url": "https://storage.googleapis.com/os-api-assignment/creative_8273.png"

}
```
### Response

```
{
    "message": "Objects processed with Vision API.",
    "objects": [
        {
            "object_name": "Bottled and jarred packaged goods",
            "url": "https://storage.googleapis.com/os-api-assignment/object_1_Bottled%20and%20jarred%20packaged%20goods_20241228003122.png"
        },
        {
            "object_name": "Bottle",
            "url": "https://storage.googleapis.com/os-api-assignment/object_2_Bottle_20241228003122.png"
        }
    ]
}
```

- Defaults to 'Bottle' (For GlowWell Skin Serum) ,if Cloud Vision API does not or could not detect any objects.

Logo Integration API - https://logo-api-141459457956.us-central1.run.app/integrate_logo - Uses Pillow and other libraries to inteagrate logo with a base image according to user preference.
### Payload
```
{
    "base_image_url": "https://storage.googleapis.com/os-api-assignment/creative_3491.png",
    "logo_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ80MR6ixOUiLl9Fp-LbMvH93M4F7bx5Q1qSg&s",
    "position": "top-right",
    "scale_factor": 0.2,
    "file_name": "processed_image.png"
}
```
### Response
```
{
    "public_url": "https://storage.googleapis.com/os-api-assignment/processed_image.png"
}
```



## **Features**
- **User Input**: Upload an image and provide additional details via a user-friendly web interface.
- **Image Generation**: 
  - The uploaded image and details are sent to an API that generates a creative poster. Creative generation using either Outpainting or Inpainting using the models in [replicate.com](https://replicate.com/).
- **Object Detection for Masking**:
  - For the given poster image objects are detected using Google Cloud Vision API, if no objects are detected, the detected objects are defaulted to 'Bottle' (For GlowWell Skin Serum)
- **Cloud Storage**: 
  - The generated poster is uploaded to **Google Cloud Storage**.
  - The **image URL** is retrieved from Google Cloud.
- **Mask Generation**:
  - The image URL is sent to lang-segment-anything API hosted in [replicate.com](https://replicate.com/) to generate a mask for the poster.
  - The mask is used to refine and customize the generated poster.
- **Logo and Mask Integration**:
  - The mask is applied to the generated poster.
  - A logo is added to the masked poster to finalize the design using the custom built logo integration API.

---

## **Technologies Used**

- **Frontend**:
  - **Streamlit and React-Vercel**: For building the web-based user interface.
  
- **Backend**:
  - **Custom APIs**: Logo-API, Cloud Vision API
  - **Google Cloud Storage**: For storing and managing images.
  - **Replicate** and **Together.ai** - Used for usage of several LLMs.
  
- **Programming Language**:
  - Python.
  - React/Js
  - Docker
  - HTML

---

## **Installation and Setup**

### **1. Prerequisites**
- Python 3.8 or higher.
- A Google Cloud Platform (GCP) account.
- Set up **Google Cloud Storage** and create a bucket.
- Ensure the required API keys are available.

