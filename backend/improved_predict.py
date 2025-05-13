import os
import argparse
import cv2
import matplotlib.pyplot as plt
import numpy as np
from improved_parts_classifier import ImprovedPartsClassifier
from pathlib import Path
import glob

def parse_args():
    parser = argparse.ArgumentParser(description='Predict spare part class from image(s)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image_path', type=str,
                        help='Path to a single image file to classify')
    group.add_argument('--image_dir', type=str,
                        help='Path to a directory of images to classify')
    parser.add_argument('--model_path', type=str, default='improved_parts_model.h5',
                        help='Path to the trained model')
    parser.add_argument('--class_map_path', type=str, default='improved_class_indices.pkl',
                        help='Path to the class indices file')
    parser.add_argument('--img_size', type=int, default=224,
                        help='Image size for model input')
    parser.add_argument('--save_visualizations', action='store_true',
                        help='Save visualization images with predictions')
    return parser.parse_args()

def display_prediction(image_path, predicted_class, confidence, save_dir=None):
    """
    Display the image with prediction results
    
    Args:
        image_path: Path to the image
        predicted_class: Predicted class name
        confidence: Prediction confidence (0-1)
        save_dir: Directory to save visualization (if None, don't save)
    """
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.title(f"Predicted: {predicted_class}\nConfidence: {confidence:.2%}")
    plt.axis('off')
    
    if save_dir:
        # Create output directory if it doesn't exist
        output_dir = Path(save_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Save the visualization
        img_name = os.path.basename(image_path)
        output_path = output_dir / f"pred_{Path(image_path).stem}.png"
        plt.savefig(output_path)
        plt.close()
        print(f"Visualization saved to {output_path}")
    else:
        plt.show()
        plt.close()

def predict_single_image(classifier, image_path, save_dir=None):
    """
    Make prediction on a single image
    
    Args:
        classifier: Trained classifier
        image_path: Path to the image file
        save_dir: Directory to save visualization (if None, don't save)
    """
    predicted_class, confidence = classifier.predict(image_path)
    
    print(f"Image: {os.path.basename(image_path)}")
    print(f"Predicted class: {predicted_class}")
    print(f"Confidence: {confidence:.2%}")
    print("-" * 50)
    
    if save_dir:
        display_prediction(image_path, predicted_class, confidence, save_dir)
    
    return predicted_class, confidence

def predict_directory(classifier, image_dir, save_dir=None):
    """
    Make predictions on all images in a directory
    
    Args:
        classifier: Trained classifier
        image_dir: Path to the directory containing images
        save_dir: Directory to save visualizations (if None, don't save)
    """
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    image_paths = []
    
    # Get all image files
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(image_dir, ext)))
    
    if not image_paths:
        print(f"No images found in {image_dir}")
        return
    
    print(f"Found {len(image_paths)} images to predict")
    
    # Process each image
    results = []
    for image_path in image_paths:
        try:
            predicted_class, confidence = predict_single_image(classifier, image_path, save_dir)
            results.append({
                'image': os.path.basename(image_path),
                'prediction': predicted_class,
                'confidence': confidence
            })
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    # Calculate statistics
    if results:
        class_counts = {}
        for result in results:
            pred = result['prediction']
            if pred in class_counts:
                class_counts[pred] += 1
            else:
                class_counts[pred] = 1
        
        print("\nSummary of predictions:")
        for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{cls}: {count} images ({count/len(results):.1%})")
    
    return results

def main():
    # Parse command-line arguments
    args = parse_args()
    
    # Create the classifier
    classifier = ImprovedPartsClassifier(
        data_dir=None,  # Not needed for prediction
        img_size=(args.img_size, args.img_size)
    )
    
    # Load the trained model
    loaded = classifier.load_model(
        model_path=args.model_path,
        class_map_path=args.class_map_path
    )
    
    if not loaded:
        print("Failed to load model. Exiting.")
        return
    
    # Determine where to save visualizations
    save_dir = None
    if args.save_visualizations:
        save_dir = "improved_predictions"
    
    # Make predictions
    if args.image_path:
        # Single image prediction
        predict_single_image(classifier, args.image_path, save_dir)
    else:
        # Directory prediction
        predict_directory(classifier, args.image_dir, save_dir)

if __name__ == '__main__':
    main() 