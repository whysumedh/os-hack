# **AdCraft : Your Ads, Your Way, All Day!**

This project enables users to generate customized posters by leveraging an API for creative generation, Google Cloud Storage for storing generated images, and multiple models. It automates the process of creating posters by combining uploaded images, masks, and logos seamlessly.

---
![image](https://github.com/user-attachments/assets/fa764a1f-22b6-4646-862d-03cb9982f7ea)


## 🔗 Demo Video
- Sped up the video to 2x

https://drive.google.com/drive/folders/1A1vtRV-iDrYIjKYmGxwpRpCNWGjBOHEt

- We realized a solution to keep the given product image intact which is outpainting (opposite of inpainting shown in the video), generate definite poster around the given product. we will be integrating the same soon.
## 🔗 Hosted Apps

- Check out the react API Interface we have created for this app: https://os-hack.vercel.app/
- Check out the Streamit App we have created for customizable image generation (Integrate your product and logos here): https://adcraft.streamlit.app/

## 🔗 Hosted APIs

All the API Codes have been uploaded to the repo with their respective folder names.

- https://creative-api-141459457956.us-central1.run.app/generate_creative - For creative generation and scoring of the creative according to the payload given.
- https://flask-api-141459457956.us-central1.run.app/remove-background - To use cloud vision API for object detection for masking of images
- https://logo-api-141459457956.us-central1.run.app/integrate_logo - Uses Pillow and other libraries to inteagrate logo with a base image according to user preference.
- We used several hosted models in [replicate.com](https://replicate.com/) as APIs

## Workflow and Architecture

![OS-HACK (1)](https://github.com/user-attachments/assets/96c85cf0-c83d-4a45-a859-55d9d9752fe1)



As discussed in the demo video, this is how an optimized product regeneration would be possible, (due to time and computational constraints we could not implement this and trying to update the below workflow model) essentially the inpainting will be done with an image prompt (instead of text description of the product image):
![image](https://github.com/user-attachments/assets/3e69b48f-3427-479b-823b-e26fbcaacfc5)


## **Features**
- **User Input**: Upload an image and provide additional details via a user-friendly web interface.
- **Image Generation**: 
  - The uploaded image and details are sent to an API that generates a creative poster.
- **Cloud Storage**: 
  - The generated poster is uploaded to **Google Cloud Storage**.
  - The **image URL** is retrieved from Google Cloud.
- **Mask Generation**:
  - The image URL is sent to another API to generate a mask for the poster.
  - The mask is used to refine and customize the generated poster.
- **Logo and Mask Integration**:
  - The mask is applied to the generated poster.
  - A logo is added to the masked poster to finalize the design.
- **Output**:
  - The final masked and logo-integrated poster is displayed and/or available for download.

---

## **Workflow**

1. **User Input**:
   - The user uploads an image and provides additional details via the Streamlit app.

2. **API for Poster Generation**:
   - The uploaded image and user-provided data are sent to a **Poster Generation API**.
   - The API generates a creative poster.

3. **Google Cloud Storage**:
   - The generated poster is uploaded to a **Google Cloud Storage bucket**.
   - The **public URL** of the uploaded poster is retrieved.

4. **Mask Generation API**:
   - The poster URL is sent to a **Mask Generation API**.
   - The API returns a mask for the poster.

5. **Final Poster Creation**:
   - The mask is applied to the poster.
   - A logo is added to the masked poster to finalize the design.

6. **Display/Download**:
   - The final poster is displayed on the app and can be downloaded by the user.

---

## **Technologies Used**

- **Frontend**:
  - **Streamlit and Rect-Vercel**: For building the web-based user interface.
  
- **Backend**:
  - **Custom APIs**: Logo-API, Cloud Vision API
  - **Google Cloud Storage**: For storing and managing images.
  - **Replicate** - Used for usage of several LLMs.
  
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

