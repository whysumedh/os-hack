# **Poster Generation and Masking with APIs and Google Cloud**

This project enables users to generate customized posters by leveraging an API for creative generation, Google Cloud Storage for storing generated images, and another API for generating masks. It automates the process of creating posters by combining uploaded images, masks, and logos seamlessly.

---

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
  - **Streamlit**: For building the web-based user interface.
  
- **Backend**:
  - Custom APIs (Poster Generation & Mask Generation APIs).
  - **Google Cloud Storage**: For storing and managing images.
  
- **Programming Language**:
  - Python.

---

## **Installation and Setup**

### **1. Prerequisites**
- Python 3.8 or higher.
- A Google Cloud Platform (GCP) account.
- Set up **Google Cloud Storage** and create a bucket.
- Ensure the required APIs (Poster Generation API and Mask Generation API) are accessible.

### **2. Clone the Repository**
```bash
git clone <repository_url>
cd <repository_folder>
