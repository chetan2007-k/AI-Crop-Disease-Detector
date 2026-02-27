"""
AI Crop Disease Detector - Model Training Script
================================================
This script trains a deep learning model using transfer learning (MobileNetV2)
to classify crop diseases from leaf images.

Dataset: PlantVillage Dataset or similar plant disease datasets
Target: 10-50 plant disease classes
Architecture: MobileNetV2 + Custom Dense Layers
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# =====================================================
# Configuration
# =====================================================
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.0001
VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42

# Path to dataset
DATASET_PATH = './dataset/'
MODEL_SAVE_PATH = './crop_model.h5'

# Disease classes (example - adjust based on your dataset)
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

def load_and_preprocess_data(dataset_path):
    """
    Load images from dataset directory and preprocess them.
    
    Expected directory structure:
    dataset/
        ├── class1/
        │   ├── image1.jpg
        │   ├── image2.jpg
        ├── class2/
        │   ├── image1.jpg
        │   ├── image2.jpg
    """
    print("Loading and preprocessing data...")
    
    images = []
    labels = []
    
    # Check if dataset directory exists
    if not os.path.exists(dataset_path):
        print(f"⚠️  Dataset directory '{dataset_path}' not found!")
        print("Please download PlantVillage dataset and place in ./dataset/")
        print("Dataset URL: https://www.kaggle.com/emmarex/plantvillage-dataset")
        print("\nCreating dummy data for testing...")
        return create_dummy_data()
    
    # Load images from subdirectories
    for class_index, disease_class in enumerate(DISEASE_CLASSES):
        class_path = os.path.join(dataset_path, disease_class)
        
        if not os.path.exists(class_path):
            print(f"⚠️  Class directory '{disease_class}' not found. Skipping...")
            continue
        
        for img_name in os.listdir(class_path):
            img_path = os.path.join(class_path, img_name)
            
            try:
                # Load and preprocess image
                img = keras.preprocessing.image.load_img(
                    img_path, target_size=(IMG_SIZE, IMG_SIZE)
                )
                img_array = keras.preprocessing.image.img_to_array(img)
                img_array = img_array / 255.0  # Normalize
                
                images.append(img_array)
                labels.append(class_index)
            except Exception as e:
                print(f"Error loading {img_path}: {str(e)}")
                continue
    
    if len(images) == 0:
        print("⚠️  No images loaded. Creating dummy data for testing...")
        return create_dummy_data()
    
    return np.array(images), np.array(labels)

def create_dummy_data():
    """
    Create dummy data for testing model architecture.
    Use this for developing without the actual dataset.
    """
    print("Creating dummy training data for testing...")
    
    # Create random dummy images
    x_train = np.random.rand(100, IMG_SIZE, IMG_SIZE, 3)
    y_train = np.random.randint(0, len(DISEASE_CLASSES), 100)
    
    return x_train, y_train

def create_model(num_classes):
    """
    Create transfer learning model using MobileNetV2.
    
    Architecture:
    - MobileNetV2 (pretrained on ImageNet) - Feature extraction
    - Global Average Pooling
    - Dense(256) + Dropout(0.5)
    - Dense(128) + Dropout(0.3)
    - Dense(num_classes) + Softmax - Classification
    """
    print("Creating transfer learning model...")
    
    # Load pretrained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model weights
    base_model.trainable = False
    
    # Create new model
    model = models.Sequential([
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
        
        # Preprocessing: normalize to [-1, 1]
        layers.Rescaling(1./127.5, offset=-1),
        
        # Base model (MobileNetV2)
        base_model,
        
        # Custom layers for classification
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def compile_model(model):
    """Compile the model with appropriate optimizer and loss."""
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def train_model(model, x_train, y_train):
    """
    Train the model with data augmentation.
    
    Data augmentation includes:
    - Random rotations
    - Random horizontal flips
    - Random zoom
    - Random shifts
    """
    print("Setting up data augmentation...")
    
    # Data augmentation for training
    train_augmentation = ImageDataGenerator(
        rotation_range=20,
        horizontal_flip=True,
        zoom_range=0.2,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        fill_mode='nearest'
    )
    
    # Split data into training and validation
    x_train_split, x_val, y_train_split, y_val = train_test_split(
        x_train, y_train, test_size=VALIDATION_SPLIT, random_state=RANDOM_SEED
    )
    
    print(f"Training set size: {len(x_train_split)}")
    print(f"Validation set size: {len(x_val)}")
    
    print("\nStarting model training...")
    
    # Callbacks
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )
    
    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=2,
        min_lr=1e-7
    )
    
    # Train the model
    history = model.fit(
        train_augmentation.flow(x_train_split, y_train_split, batch_size=BATCH_SIZE),
        validation_data=(x_val, y_val),
        epochs=EPOCHS,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )
    
    return model, history

def evaluate_model(model, x_test, y_test):
    """Evaluate model on test dataset."""
    print("\nEvaluating model on test set...")
    loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
    print(f"Test Loss: {loss:.4f}")
    print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    return loss, accuracy

def save_model(model, save_path):
    """Save the trained model."""
    print(f"\nSaving model to {save_path}...")
    model.save(save_path)
    print(f"✓ Model saved successfully!")

def main():
    """Main training pipeline."""
    print("=" * 60)
    print("AI CROP DISEASE DETECTOR - MODEL TRAINING")
    print("=" * 60 + "\n")
    
    # Set random seed for reproducibility
    np.random.seed(RANDOM_SEED)
    tf.random.set_seed(RANDOM_SEED)
    
    # Load and preprocess data
    x_data, y_data = load_and_preprocess_data(DATASET_PATH)
    print(f"Loaded {len(x_data)} images from {len(DISEASE_CLASSES)} classes")
    
    # Split into train and test sets
    x_train, x_test, y_train, y_test = train_test_split(
        x_data, y_data, test_size=0.1, random_state=RANDOM_SEED
    )
    
    # Create model
    num_classes = len(DISEASE_CLASSES)
    model = create_model(num_classes)
    
    # Compile model
    model = compile_model(model)
    
    # Print model summary
    print("\nModel Architecture:")
    model.summary()
    
    # Train model
    model, history = train_model(model, x_train, y_train)
    
    # Evaluate model
    evaluate_model(model, x_test, y_test)
    
    # Save model
    save_model(model, MODEL_SAVE_PATH)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
