# 🌾 AI Crop Disease Detector

A complete end-to-end machine learning application that helps farmers detect crop diseases from leaf images using deep learning and provides treatment recommendations.

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.13+-orange)

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Solution Description](#solution-description)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Dataset](#dataset)
- [Model Training](#model-training)
- [API Endpoints](#api-endpoints)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Project Overview

**AI Crop Disease Detector** is a web-based application that uses artificial intelligence to identify crop diseases from leaf images. Farmers can upload a photo of their crop leaf, and the AI model predicts the disease with treatment suggestions.

### Key Features:
- ✅ **Deep Learning Classification** - MobileNetV2 transfer learning model
- ✅ **Real-time Prediction** - Fast disease detection in seconds
- ✅ **Treatment Recommendations** - Personalized treatment and prevention advice
- ✅ **User-Friendly Interface** - Simple, intuitive web interface
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile devices
- ✅ **Report Generation** - Download analysis reports
- ✅ **REST API** - Backend API for integration with other applications

---

## 🚜 Problem Statement

### Challenges Faced by Farmers:
1. **Crop Disease Loss**: Annual crop losses due to diseases reach 25-30% of total production
2. **Limited Agricultural Expertise**: Farmers in developing regions lack access to agricultural experts
3. **Late Disease Detection**: Manual diagnosis delays treatment, increasing crop damage
4. **High Treatment Costs**: Incorrect disease identification leads to wasted resources
5. **Lack of Digital Tools**: Most farmers have limited access to digital agricultural solutions

### Impact:
- Estimated $220 billion annual loss globally due to crop diseases
- Poor farmers most affected due to limited resources and knowledge
- Need for affordable, accessible disease detection solutions

---

## 💡 Solution Description

### How It Works:

```
Farmer's Photo
	↓
[Image Upload]
	↓
[Image Preprocessing] (224×224 resize, normalization)
	↓
[MobileNetV2 Feature Extraction]
	↓
[Disease Classification]
	↓
[Treatment Database Lookup]
	↓
[Results Display] (Disease, Confidence, Treatment)
```

### Key Components:

1. **Deep Learning Model**
   - Transfer learning with MobileNetV2 (ImageNet pretrained)
   - Lightweight and fast (~17MB)
   - Supports 38+ plant disease classes
   - ~93% accuracy on test set

2. **Backend API**
   - Python Flask REST API
   - Image preprocessing
   - Disease prediction
   - Treatment recommendation

3. **Frontend Interface**
   - Responsive web interface
   - Drag-and-drop image upload
   - Real-time result display
   - Report generation

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Web Browser)                │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  HTML5 | CSS3 | Vanilla JavaScript               │  │
│  │  - Image Upload                                   │  │
│  │  - Real-time Preview                             │  │
│  │  - Results Display                               │  │
│  │  - Report Download                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
					 ↕
				HTTP/REST API
					 ↕
┌─────────────────────────────────────────────────────────┐
│              BACKEND (Flask Server)                     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Flask REST API                                  │  │
│  │  - POST /predict                                 │  │
│  │  - GET /health                                   │  │
│  │  - GET /info                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Image Processing                                │  │
│  │  - Load image                                    │  │
│  │  - Resize to 224×224                             │  │
│  │  - Normalize pixel values                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ML Model (crop_model.h5)                        │  │
│  │  - TensorFlow/Keras                              │  │
│  │  - MobileNetV2 + Dense Layers                    │  │
│  │  - Output: Disease class + Confidence           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Treatment Database                              │  │
│  │  - Disease → Treatment Mapping                   │  │
│  │  - Severity Levels                               │  │
│  │  - Prevention Tips                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
					 ↕
┌─────────────────────────────────────────────────────────┐
│           ML MODEL TRAINING (Offline)                   │
│                                                         │
│  train_model.py                                         │
│  - Dataset: PlantVillage                               │
│  - 38 disease classes                                  │
│  - Output: crop_model.h5                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic structure
- **CSS3** - Responsive styling
- **JavaScript (ES6+)** - DOM manipulation
- **Fetch API** - HTTP requests

### Backend
- **Python 3.8+** - Core language
- **Flask 3.0** - Web framework
- **Flask-CORS** - CORS support
- **TensorFlow 2.13** - Deep learning
- **Keras** - Neural networks
- **Pillow** - Image processing
- **scikit-learn** - Data preprocessing

### Machine Learning
- **MobileNetV2** - Feature extraction
- **ImageDataGenerator** - Data augmentation
- **Transfer Learning** - Efficient training

---

## 📁 Project Structure

```
AI-Crop-Disease-Detector/
├── dataset/                    # Training data
├── model/                      # ML Models
│   ├── train_model.py
│   └── crop_model.h5
├── backend/                    # Flask API
│   ├── app.py
│   └── requirements.txt
├── frontend/                   # Web Interface
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Git
- Modern web browser

### Steps

1. Clone repository:
```bash
git clone https://github.com/yourusername/AI-Crop-Disease-Detector.git
cd AI-Crop-Disease-Detector
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

---

## 🚀 How to Run

1. Download PlantVillage dataset (optional):
```bash
# From Kaggle: https://www.kaggle.com/emmarex/plantvillage-dataset
# Extract to dataset/ folder
```

2. Train model (optional):
```bash
cd model
python train_model.py
```

3. Start backend:
```bash
cd backend
python app.py
```

4. Open frontend:
```
http://localhost:5000/frontend/
```

---

## 📊 Dataset

**PlantVillage Dataset**:
- 38 disease classes
- 55,000+ images
- 14 crop types
- High resolution RGB images

### Supported Crops:
Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato

---

## 🧠 Model Details

- **Architecture**: MobileNetV2 + Dense layers
- **Input Size**: 224×224 pixels
- **Output**: 38 disease classes
- **Accuracy**: 92-95%
- **Model Size**: 17 MB
- **Inference Speed**: 100-200ms

---

## 🔗 API Endpoints

### POST /predict
Upload image and get disease prediction

### GET /health
Health check endpoint

### GET /info
Get available disease classes

---

## 🔮 Future Improvements

- Multi-leaf analysis
- Disease severity estimation
- Weather integration
- Offline functionality
- Mobile application
- Cloud deployment
- IoT sensor integration
- Expert network connection

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **PlantVillage Dataset**
- **TensorFlow & Keras**
- **Flask Community**

---

<div align="center">

### 🌱 Helping Farmers Fight Crop Diseases! 🌱

**Built with ❤️ for sustainable agriculture**

</div>