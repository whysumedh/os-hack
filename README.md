# **AdCraft : Your Ads, Your Way, All Day!**

This project enables users to generate customized posters by leveraging an API for creative generation, Google Cloud Storage for storing generated images, and multiple models. It automates the process of creating posters by combining uploaded images, masks, and logos seamlessly.

---
![image](https://github.com/user-attachments/assets/f6559450-a3f2-4a57-824a-dd51b6d1d108)

## 🔗 Demo Video
https://drive.google.com/drive/folders/1A1vtRV-iDrYIjKYmGxwpRpCNWGjBOHEt

- As mentioned in the video we have updated our scoring method in the code.
## 🔗 Hosted Apps

- Check out the react API Interface we have created for this app: https://os-hack.vercel.app/
- Check out the Streamit App we have created for customizable image generation (Integrate your product and logos here): https://adcraft.streamlit.app/

## 🔗 Hosted APIs

All the API Codes have been uploaded to the repo with their respective folder names.

- https://creative-api-141459457956.us-central1.run.app/generate_creative - For creative generation according to the payload given.
- https://flask-api-141459457956.us-central1.run.app/remove-background - To use cloud vision API for object detection for masking of images
- https://logo-integration-api-141459457956.us-central1.run.app/integrate_logo - Uses Pillow and other libraries to inteagrate logo with a base image according to user preference.

## Workflow and Architecture

![image](https://github.com/user-attachments/assets/3b0ddf0c-a6f5-4652-a033-b8d635d1e982)



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

