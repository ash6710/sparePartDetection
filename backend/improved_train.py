import os
import argparse
from improved_parts_classifier import ImprovedPartsClassifier
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description='Train an improved spare parts classifier')
    parser.add_argument('--data_dir', type=str, default='parts_images',
                        help='Directory containing class folders with images')
    parser.add_argument('--img_size', type=int, default=224,
                        help='Image size for model input')
    parser.add_argument('--batch_size', type=int, default=16,
                        help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=15,
                        help='Number of initial training epochs')
    parser.add_argument('--fine_tune_epochs', type=int, default=15,
                        help='Number of fine-tuning epochs')
    parser.add_argument('--model_choice', type=str, default='resnet', 
                        choices=['resnet', 'efficientnet'],
                        help='Base model to use (resnet, efficientnet)')
    parser.add_argument('--model_path', type=str, default='improved_parts_model.h5',
                        help='Path to save the trained model')
    parser.add_argument('--validation_split', type=float, default=0.2,
                        help='Validation split ratio (0-1)')
    parser.add_argument('--visualize', action='store_true',
                        help='Visualize predictions after training')
    return parser.parse_args()

def plot_training_history(history, save_path='improved_training_history.png'):
    # Plot training & validation accuracy values
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    # Plot training & validation loss values
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    
    print(f"Training history plot saved to {save_path}")

def main():
    # Parse command-line arguments
    args = parse_args()
    
    print(f"Using {args.model_choice} as base model")
    
    # Create the classifier
    classifier = ImprovedPartsClassifier(
        data_dir=args.data_dir,
        img_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        model_choice=args.model_choice
    )
    
    # Load the data
    classifier.load_data(validation_split=args.validation_split)
    
    # Build the model
    classifier.build_model()
    
    # Train the model
    history = classifier.train(epochs=args.epochs, fine_tune_epochs=args.fine_tune_epochs)
    
    # Save the model
    classifier.save_model(model_path=args.model_path)
    
    # Plot training history
    plot_training_history(history)
    
    # Evaluate the model on the validation set
    metrics = classifier.evaluate()
    print(f"Final validation accuracy: {metrics['accuracy']:.4f}")
    
    # Visualize predictions if requested
    if args.visualize:
        classifier.visualize_predictions(num_images=5)
    
    print(f"Training complete! Model saved to {args.model_path}")

if __name__ == '__main__':
    main() 