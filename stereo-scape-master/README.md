# 🌟 StereoScape - 3D Model Generator

A powerful web application that transforms 2D images and videos into stunning 3D models using NeRF (Neural Radiance Fields) technology. StereoScape provides an intuitive interface for converting your 2D content into immersive 3D experiences.

![WhatsApp Image 2025-04-23 at 18 49 21_29c7879c](https://github.com/user-attachments/assets/40723ff4-b973-4e10-be73-8adbabbbd577)



## 🎯 Overview

StereoScape leverages cutting-edge Neural Radiance Fields (NeRF) technology to:
- Convert 2D images/videos into detailed 3D models
- Generate high-resolution outputs (up to 4k)
- Provide realistic rendering with accurate lighting and shadows
- Enable novel view synthesis for immersive exploration

## 📸 Application Screenshots

### Upload Interface
![WhatsApp Image 2025-04-23 at 18 50 05_32dc89a8](https://github.com/user-attachments/assets/eef52400-c5c9-4ed2-9e5d-178a849f608c)


### Processing View with PSNR Graph
![WhatsApp Image 2025-04-25 at 22 29 05_e5add29b](https://github.com/user-attachments/assets/2b48c71b-f837-4e95-abfa-936fbdd3b530)


### NeRF Information
![WhatsApp Image 2025-04-23 at 18 49 52_62f1f288](https://github.com/user-attachments/assets/84f7611b-0f6c-4ada-8d00-6b88aa316275)




## 🚀 Key Features

- **Intuitive Upload Interface**: Simple drag-and-drop functionality for images/videos
- **Real-time Processing**: Watch your 3D model come to life with progress tracking
- **High-Quality Output**: Generate detailed 3D models with realistic textures
- **Interactive Viewing**: Explore your 3D models from any angle
- **Fluid Animations**: Smooth user experience with beautiful visual effects
- **PSNR Tracking**: Real-time Peak Signal-to-Noise Ratio monitoring
- **Multi-view Processing**: Support for multiple image angles

## 💻 Technology Stack

### Frontend
- SvelteKit
- TypeScript
- Tailwind CSS
- WebGL animations

### Backend
- Python Flask
- COLMAP
- TensorFlow
- MongoDB

## 🛠️ Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/nilay2004/steroscape.git
   ```

2. Backend Setup:
   ```bash
   cd stereo-scape/backend
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   python app.py
   ```

3. Frontend Setup:
   ```bash
   cd ../web
   npm install
   npm run dev
   ```

## 🔗 Connect With Me

- **Created by**: Nilay Pandya
- **LinkedIn**: [Nilay Pandya](https://www.linkedin.com/in/nilay-pandya-b6ba62253/)
- **GitHub**: [nilay2004](https://github.com/nilay2004/steroscape)



If you find this project helpful, please consider giving it a ⭐️
