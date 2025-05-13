import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50V2, EfficientNetV2L
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
from tqdm import tqdm
import cv2


class ImprovedPartsClassifier:
    def __init__(self, data_dir, img_size=(224, 224), batch_size=16, model_choice='resnet'):
        """
        Initialize the improved spare part classifier.
        
        Args:
            data_dir: Directory containing class folders with images
            img_size: Input image size for the model (default: 224x224)
            batch_size: Batch size for training (default: 16)
            model_choice: Base model to use ('resnet', 'efficientnet')
        """
        self.data_dir = data_dir
        self.img_size = img_size
        self.batch_size = batch_size
        self.model_choice = model_choice
        self.model = None
        self.class_names = []
        self.class_indices = {}
        
    def load_data(self, validation_split=0.2):
        """
        Load and preprocess image data from directories
        """
        print("Loading and preparing data...")
        
        # Get class names from directory structure
        self.class_names = [d for d in os.listdir(self.data_dir) 
                           if os.path.isdir(os.path.join(self.data_dir, d))]
        
        print(f"Found {len(self.class_names)} classes")
        
        # Create image data generators with augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split,
            rotation_range=30,        # More rotation for varied angles
            width_shift_range=0.15,   # Slightly increased shift
            height_shift_range=0.15,  # Slightly increased shift
            shear_range=0.15,         # Slightly increased shear
            zoom_range=0.2,           # More zoom variation
            brightness_range=[0.8, 1.2],  # Add brightness variation
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Validation generator with just rescaling
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split
        )
        
        # Training generator
        self.train_generator = train_datagen.flow_from_directory(
            self.data_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        # Validation generator (using val_datagen to avoid augmentation on validation)
        self.validation_generator = val_datagen.flow_from_directory(
            self.data_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        # Save class indices for inference later
        self.class_indices = self.train_generator.class_indices
        self.class_names = list(self.class_indices.keys())
        
        # Reverse the dictionary to map indices to class names
        self.idx_to_class = {v: k for k, v in self.class_indices.items()}
        
        print(f"Prepared {self.train_generator.samples} training samples")
        print(f"Prepared {self.validation_generator.samples} validation samples")
        
        return self.train_generator, self.validation_generator
        
    def build_model(self):
        """
        Build a transfer learning model using ResNet50V2 or EfficientNetV2L as base
        """
        print(f"Building model with {self.model_choice} as base...")
        num_classes = len(self.class_names)
        
        # Create base pre-trained model
        if self.model_choice == 'resnet':
            base_model = ResNet50V2(weights='imagenet', include_top=False, input_shape=(*self.img_size, 3))
        elif self.model_choice == 'efficientnet':
            base_model = EfficientNetV2L(weights='imagenet', include_top=False, input_shape=(*self.img_size, 3))
        else:
            raise ValueError("model_choice must be 'resnet' or 'efficientnet'")
        
        # Freeze the base model layers
        for layer in base_model.layers:
            layer.trainable = False
            
        # Add custom classification head
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        x = Dropout(0.5)(x)  # Higher dropout to prevent overfitting
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(num_classes, activation='softmax')(x)
        
        # Create the final model
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        # Store the base model for later use in fine-tuning
        self.base_model = base_model
        
        # Compile the model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(f"Model built with {len(self.class_names)} output classes")
        return self.model
    
    def train(self, epochs=15, fine_tune_epochs=15):
        """
        Train the model with a two-phase approach: feature extraction and fine-tuning
        
        Args:
            epochs: Number of initial training epochs (feature extraction phase)
            fine_tune_epochs: Number of fine-tuning epochs
        """
        if self.model is None:
            self.build_model()
            
        # Set up callbacks
        checkpoint = ModelCheckpoint(
            'improved_model_checkpoint.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        early_stopping = EarlyStopping(
            monitor='val_accuracy',
            patience=7,  # More patience
            restore_best_weights=True,
            mode='max',
            verbose=1
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
        
        callbacks = [checkpoint, early_stopping, reduce_lr]
        
        # Phase 1: Train with frozen base model (feature extraction)
        print("Phase 1: Training with frozen base model (feature extraction)...")
        history = self.model.fit(
            self.train_generator,
            steps_per_epoch=self.train_generator.samples // self.batch_size,
            validation_data=self.validation_generator,
            validation_steps=self.validation_generator.samples // self.batch_size,
            epochs=epochs,
            callbacks=callbacks
        )
        
        # Phase 2: Fine-tuning - unfreeze some layers and train with lower learning rate
        print("Phase 2: Fine-tuning with selected layers unfrozen...")
        
        # Unfreeze layers for fine-tuning
        if self.model_choice == 'resnet':
            # For ResNet, unfreeze the last conv block (stage 5)
            for layer in self.base_model.layers[-30:]:  # Last 30 layers (approximately last block for ResNet50V2)
                layer.trainable = True
        else:
            # For EfficientNet, unfreeze the last few blocks
            for layer in self.base_model.layers[-50:]:  # Last 50 layers
                layer.trainable = True
        
        # Recompile with much lower learning rate for fine-tuning
        self.model.compile(
            optimizer=Adam(learning_rate=1e-5),  # Much lower learning rate
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Print model summary after unfreezing
        self.model.summary()
        
        # Continue training with fine-tuning
        fine_tune_history = self.model.fit(
            self.train_generator,
            steps_per_epoch=self.train_generator.samples // self.batch_size,
            validation_data=self.validation_generator,
            validation_steps=self.validation_generator.samples // self.batch_size,
            epochs=fine_tune_epochs,
            callbacks=callbacks
        )
        
        # Combine histories
        combined_history = {}
        for key in history.history:
            combined_history[key] = history.history[key] + fine_tune_history.history[key]
            
        return type('History', (), {'history': combined_history})
    
    def save_model(self, model_path='improved_parts_model.h5', class_map_path='improved_class_indices.pkl'):
        """
        Save the trained model and class indices
        """
        if self.model is None:
            print("No model to save. Please train the model first.")
            return False
            
        # Save model
        self.model.save(model_path)
        
        # Save class indices
        with open(class_map_path, 'wb') as f:
            pickle.dump(self.class_indices, f)
            
        print(f"Model saved to {model_path}")
        print(f"Class indices saved to {class_map_path}")
        return True
    
    def load_model(self, model_path='improved_parts_model.h5', class_map_path='improved_class_indices.pkl'):
        """
        Load a trained model and class indices
        """
        # Load the model
        try:
            self.model = tf.keras.models.load_model(model_path)
            print(f"Model loaded from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
            
        # Load class indices
        try:
            with open(class_map_path, 'rb') as f:
                self.class_indices = pickle.load(f)
                
            self.idx_to_class = {v: k for k, v in self.class_indices.items()}
            self.class_names = list(self.class_indices.keys())
            print(f"Class indices loaded from {class_map_path}")
        except Exception as e:
            print(f"Error loading class indices: {e}")
            return False
            
        return True
    
    def predict(self, image_path):
        """
        Predict the class of a single image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            predicted_class: The predicted class name
            confidence: The confidence score for the prediction
        """
        if self.model is None:
            print("No model loaded. Please load or train a model first.")
            return None, 0
            
        # Load and preprocess the image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        img = cv2.resize(img, self.img_size)  # Resize to model input size
        img = img / 255.0  # Normalize
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        
        # Make prediction
        predictions = self.model.predict(img)
        pred_idx = np.argmax(predictions, axis=1)[0]
        confidence = predictions[0][pred_idx]
        
        # Get the class name
        if self.idx_to_class and pred_idx in self.idx_to_class:
            predicted_class = self.idx_to_class[pred_idx]
        else:
            predicted_class = f"Class {pred_idx}"
            
        return predicted_class, float(confidence)
    
    def evaluate(self, test_dir=None):
        """
        Evaluate the model on the validation set
        
        Args:
            test_dir: Optional directory with test images. If None, uses validation set.
            
        Returns:
            Dictionary with metrics
        """
        if self.model is None:
            print("No model loaded. Please load or train a model first.")
            return None
            
        if test_dir is None:
            print("Evaluating on validation set...")
            metrics = self.model.evaluate(
                self.validation_generator,
                steps=self.validation_generator.samples // self.batch_size + 1
            )
            return {'loss': metrics[0], 'accuracy': metrics[1]}
        
        # If test_dir is provided, create a test generator and evaluate
        print(f"Evaluating on test set {test_dir}...")
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        metrics = self.model.evaluate(
            test_generator,
            steps=test_generator.samples // self.batch_size + 1
        )
        
        return {'loss': metrics[0], 'accuracy': metrics[1]}
    
    def visualize_predictions(self, num_images=10):
        """
        Visualize model predictions on random validation images
        
        Args:
            num_images: Number of images to visualize
        """
        if self.model is None or self.validation_generator is None:
            print("Model or validation data not available.")
            return
            
        # Get some validation images
        validation_images, validation_labels = next(self.validation_generator)
        
        # Limit to the number of images requested
        num_to_display = min(num_images, len(validation_images))
        
        # Make predictions
        predictions = self.model.predict(validation_images[:num_to_display])
        
        # Plot the images with their predictions
        plt.figure(figsize=(15, 4 * num_to_display))
        
        for i in range(num_to_display):
            plt.subplot(num_to_display, 3, i*3 + 1)
            plt.imshow(validation_images[i])
            plt.axis('off')
            
            # True label
            true_label_idx = np.argmax(validation_labels[i])
            true_label = self.idx_to_class.get(true_label_idx, f"Class {true_label_idx}")
            
            # Predicted label
            pred_idx = np.argmax(predictions[i])
            pred_label = self.idx_to_class.get(pred_idx, f"Class {pred_idx}")
            confidence = predictions[i][pred_idx]
            
            # Set title color based on correctness
            title_color = 'green' if pred_idx == true_label_idx else 'red'
            
            plt.title(f"True: {true_label}\nPred: {pred_label}\nConf: {confidence:.2f}", 
                     color=title_color)
            
        plt.tight_layout()
        plt.savefig('prediction_visualization.png')
        plt.close()
        print("Prediction visualization saved to 'prediction_visualization.png'") 