import os
import io
import time
import json
import numpy as np
import cv2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from improved_parts_classifier import ImprovedPartsClassifier
import uvicorn
import tensorflow as tf

# Initialize the FastAPI app
app = FastAPI(
    title="Spare Parts Image Classifier API",
    description="API for classifying spare parts in images",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, modify in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the classifier globally for faster predictions
model_path = "improved_parts_modelv4.h5"
details_json_path = "Details.json"
IMG_SIZE = (224, 224)  # Default model input size

# Load part details from JSON file
try:
    with open(details_json_path, 'r') as f:
        parts_details = json.load(f)
    print(f"Parts details loaded from {details_json_path}")
    
    # Create a mapping from class indices to part names based on the index in the JSON
    idx_to_class = {part["index"]: part["part_name"] for part in parts_details}
    print(f"Created mapping for {len(idx_to_class)} classes from Details.json")
except Exception as e:
    print(f"Error loading parts details: {e}")
    parts_details = []
    idx_to_class = {}

# Track the loading time
loading_start = time.time()

# Initialize the classifier
classifier = ImprovedPartsClassifier(
    data_dir=None,  # Not needed for prediction
    img_size=IMG_SIZE
)

# Load the model but without relying on the class indices from pkl
try:
    # Load the model directly using TensorFlow
    if os.path.exists(model_path):
        classifier.model = tf.keras.models.load_model(model_path)
        # Override the classifier's idx_to_class with our JSON-based mapping
        classifier.idx_to_class = idx_to_class
        print("Model loaded successfully")
    else:
        raise FileNotFoundError(f"Model file {model_path} not found")
except Exception as e:
    raise RuntimeError(f"Failed to load model from {model_path}: {str(e)}")

loading_time = time.time() - loading_start
print(f"Model loaded successfully in {loading_time:.2f} seconds")

# Response model
class PredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    processing_time: float
    part_details: dict = None

@app.get("/")
async def root():
    return {"message": "Spare Parts Image Classifier API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": classifier.model is not None,
        "model_path": model_path,
        "details_json_loaded": len(parts_details) > 0,
        "class_mapping_count": len(idx_to_class)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    # Start the timer
    start_time = time.time()
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.jpg', '.jpeg', '.png']:
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload JPG or PNG images.")
    
    try:
        # Read the image file
        contents = await file.read()
        image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size
        image_resized = cv2.resize(image_rgb, IMG_SIZE)
        
        # Normalize
        image_normalized = image_resized / 255.0
        
        # Add batch dimension
        image_batch = np.expand_dims(image_normalized, axis=0)
        
        # Make prediction
        predictions = classifier.model.predict(image_batch)
        pred_idx = np.argmax(predictions, axis=1)[0]
        confidence = float(predictions[0][pred_idx])
        
        # Get the class name from our JSON-based mapping
        predicted_class = idx_to_class.get(int(pred_idx), f"Unknown Class {pred_idx}")
        
        # Find matching part details directly from parts_details
        part_details = None
        for part in parts_details:
            if part.get("index") == int(pred_idx):
                part_details = part
                break
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "processing_time": processing_time,
            "part_details": part_details
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 