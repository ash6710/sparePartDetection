// modelService.ts
import * as tf from '@tensorflow/tfjs';
import { getClassName } from '../utils/classMapping';

class ModelService {
  private model: tf.GraphModel | null = null;
  private isModelLoaded: boolean = false;

  async loadModel(modelPath: string): Promise<void> {
    try {
      this.model = await tf.loadGraphModel(modelPath);
      this.isModelLoaded = true;
      console.log('Model loaded successfully');
    } catch (error) {
      console.error('Error loading model:', error);
      throw error;
    }
  }

  async predict(imageElement: HTMLImageElement): Promise<{ class: number; confidence: number }> {
    if (!this.model || !this.isModelLoaded) {
      throw new Error('Model not loaded');
    }

    try {
      // Preprocess the image
      const tensor = tf.browser.fromPixels(imageElement)
        .resizeBilinear([224, 224]) // Adjust size based on your model's requirements
        .expandDims(0)
        .toFloat()
        .div(255.0);

      // Make prediction - GraphModel uses execute instead of predict
      const predictions = await this.model.execute(tensor) as tf.Tensor;
      const scores = await predictions.data();

      // Get the class with highest confidence
      const maxScore = Math.max(...scores);
      const predictedClassIndex = scores.indexOf(maxScore); // Get the index

      // Clean up tensors
      tensor.dispose();
      predictions.dispose();

      return {
        class: predictedClassIndex, // Return the numerical index
        confidence: maxScore
      };
    } catch (error) {
      console.error('Error making prediction:', error);
      throw error;
    }
  }

  isModelReady(): boolean {
    return this.isModelLoaded;
  }
}

export const modelService = new ModelService();