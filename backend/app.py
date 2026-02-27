"""
AI Crop Disease Detector - Flask Backend API
==============================================
This Flask application provides REST API endpoints for crop disease prediction.

Endpoints:
- POST /predict: Upload image and get disease prediction with treatment advice
- GET /health: Health check endpoint
"""

import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow import keras
from werkzeug.utils import secure_filename
from PIL import Image
import io
import json
from flask import send_from_directory

# =====================================================
# Configuration
# =====================================================
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMG_SIZE = 224
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Model path
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model', 'crop_model.h5'))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =====================================================
# Disease Classes and Treatment Information
# =====================================================
DISEASE_CLASSES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry___Powdery_mildew',
    'Cherry___healthy',
    'Corn___Cercospora_leaf_spot',
    'Corn___Common_rust',
    'Corn___Northern_Leaf_Blight',
    'Corn___healthy',
    'Grape___Black_rot',
    'Grape___Esca',
    'Grape___Leaf_blight',
    'Grape___healthy',
    'Orange___Haunglongbing',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper___Bacterial_spot',
    'Pepper___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

# Treatment recommendations for diseases
TREATMENT_GUIDE = {
    'Apple_scab': {
        'severity': 'Medium',
        'description': 'Fungal infection causing dark lesions on leaves and fruits',
        'treatment': [
            'Remove infected leaves and branches',
            'Apply fungicide (Sulfur or Copper-based)',
            'Improve tree ventilation',
            'Avoid wetting foliage during irrigation'
        ],
        'prevention': [
            'Use resistant varieties',
            'Practice good sanitation',
            'Apply preventive fungicides in spring'
        ]
    },
    'Black_rot': {
        'severity': 'High',
        'description': 'Fungal disease causing dark lesions and cankers',
        'treatment': [
            'Remove infected branches and fruit',
            'Prune to improve air circulation',
            'Apply copper fungicide',
            'Burn or destroy infected plant material'
        ],
        'prevention': [
            'Plant resistant varieties',
            'Maintain proper sanitation',
            'Avoid injury to trees'
        ]
    },
    'Cedar_apple_rust': {
        'severity': 'Medium',
        'description': 'Rust infection causing yellow/orange lesions',
        'treatment': [
            'Apply sulfur or copper fungicide',
            'Remove rust-infected cedar trees nearby',
            'Improve tree ventilation',
            'Remove galls from cedar trees'
        ],
        'prevention': [
            'Keep distance from cedar trees',
            'Use resistant apple varieties',
            'Regular inspections'
        ]
    },
    'Powdery_mildew': {
        'severity': 'Medium',
        'description': 'White powdery coating on leaves indicating fungal infection',
        'treatment': [
            'Apply sulfur dust or spray',
            'Use potassium bicarbonate fungicide',
            'Remove heavily infected leaves',
            'Improve air circulation'
        ],
        'prevention': [
            'Maintain proper spacing',
            'Avoid high nitrogen fertilization',
            'Regular monitoring'
        ]
    },
    'Early_blight': {
        'severity': 'High',
        'description': 'Fungal disease causing brown concentric lesions on leaves',
        'treatment': [
            'Remove infected leaves promptly',
            'Apply copper or chlorothalonil fungicide',
            'Stake plants for better air circulation',
            'Water at soil level, not foliage'
        ],
        'prevention': [
            'Use resistant varieties',
            'Mulch to prevent soil splash',
            'Rotate crops annually'
        ]
    },
    'Late_blight': {
        'severity': 'Very High',
        'description': 'Serious fungal disease causing water-soaked lesions',
        'treatment': [
            'Remove infected leaves and fruits immediately',
            'Apply metalaxyl-based fungicide',
            'Improve drainage',
            'Ensure proper plant spacing'
        ],
        'prevention': [
            'Plant resistant varieties',
            'Use certified disease-free seeds',
            'Scout for disease regularly',
            'Avoid overhead watering'
        ]
    },
    'healthy': {
        'severity': 'None',
        'description': 'No disease detected - plant appears healthy',
        'treatment': [
            'Continue regular monitoring',
            'Maintain proper watering schedule',
            'Ensure adequate sunlight',
            'Regular pest inspection'
        ],
        'prevention': [
            'Maintain good garden hygiene',
            'Provide proper nutrition',
            'Monitor for early symptoms of disease'
        ]
    }
}

# Global model variable
model = None

# =====================================================
# Model Loading
# =====================================================
def load_model():
    """Load the trained model on application startup."""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            print(f"Loading model from {MODEL_PATH}...")
            model = keras.models.load_model(MODEL_PATH)
            print("✓ Model loaded successfully!")
            return True
        else:
            print(f"⚠️  Model file not found at {MODEL_PATH}")
            print("Please train the model first using train_model.py")
            return False
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return False

# =====================================================
# Utility Functions
# =====================================================
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """
    Load and preprocess image for model prediction.
    
    Steps:
    1. Load image
    2. Resize to 224x224
    3. Normalize to [0, 1]
    """
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        
        # Resize to required dimensions
        img = img.resize((IMG_SIZE, IMG_SIZE))
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Normalize to [0, 1]
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        raise Exception(f"Image preprocessing failed: {str(e)}")

def get_disease_info(disease_name):
    """Get treatment information for a disease."""
    # Extract disease name from class label
    disease = disease_name.split('___')[-1]
    
    # Find matching treatment info (case-insensitive)
    for key, info in TREATMENT_GUIDE.items():
        if key.lower() == disease.lower():
            return info
    
    # Return generic info if not found
    return TREATMENT_GUIDE.get('healthy', {})

def format_prediction_response(class_index, confidence):
    """Format prediction into a user-friendly response."""
    disease_class = DISEASE_CLASSES[class_index]
    crop, disease = disease_class.split('___')
    
    # Get treatment information
    disease_info = get_disease_info(disease_class)
    
    return {
        'success': True,
        'crop': crop,
        'disease': disease,
        'confidence': f"{float(confidence):.2f}%",
        'confidence_value': float(confidence),
        'severity': disease_info.get('severity', 'Unknown'),
        'description': disease_info.get('description', ''),
        'treatment': disease_info.get('treatment', []),
        'prevention': disease_info.get('prevention', [])
    }

# =====================================================
# API Routes
# =====================================================
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'model_loaded': model is not None
    }), 200

@app.route('/', methods=['GET'])
def serve_frontend_root():
    """Serve frontend index page."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/frontend/', methods=['GET'])
def serve_frontend_index():
    """Serve frontend index page from /frontend/ path."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/frontend/<path:filename>', methods=['GET'])
def serve_frontend_assets(filename):
    """Serve frontend static assets (css/js/images)."""
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/predict', methods=['POST'])
def predict():
    """
    POST /predict
    
    Predict disease from uploaded image.
    
    Request:
    - Form data with 'file' field containing image
    
    Response:
    {
        "success": true,
        "crop": "Tomato",
        "disease": "Early_blight",
        "confidence": "94.23%",
        "severity": "High",
        "description": "Fungal disease...",
        "treatment": [...],
        "prevention": [...]
    }
    """
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please start the server with a trained model.'
            }), 500
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided. Please upload an image.'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected.'
            }), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Preprocess image
        img_array = preprocess_image(filepath)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        
        # Get top prediction
        class_index = np.argmax(predictions[0])
        confidence = predictions[0][class_index] * 100
        
        # Format response
        response = format_prediction_response(class_index, confidence)
        
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/info', methods=['GET'])
def get_info():
    """Get information about available disease classes."""
    return jsonify({
        'total_classes': len(DISEASE_CLASSES),
        'classes': DISEASE_CLASSES,
        'upload_size_limit_mb': MAX_FILE_SIZE / (1024 * 1024),
        'supported_formats': list(ALLOWED_EXTENSIONS)
    }), 200

# =====================================================
# Error Handlers
# =====================================================
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.0f} MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 not found."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server error."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# =====================================================
# Application Startup
# =====================================================
@app.before_request
def before_request():
    """Initialize model on first request."""
    global model
    if model is None:
        load_model()

if __name__ == '__main__':
    print("=" * 60)
    print("AI CROP DISEASE DETECTOR - BACKEND API")
    print("=" * 60)
    print("\nLoading model...")
    
    # Load model before starting server
    load_model()
    
    print("\n✓ Starting Flask server...")
    print("API Documentation:")
    print("  - Health Check: GET http://localhost:5000/health")
    print("  - Predict Disease: POST http://localhost:5000/predict (send image)")
    print("  - Get Classes: GET http://localhost:5000/info")
    print("\nOpen frontend at: http://localhost:5000/frontend/")
    print("=" * 60 + "\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
