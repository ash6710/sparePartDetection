# Sparepart Detection Web Application

This web application provides a tool to detect various spare parts for generators using a machine learning model. The application features both image upload and camera capture capabilities.

## Features

- **Image Upload**: Upload images of spare parts for detection
- **Camera Capture**: Use your device's camera to directly capture images of spare parts for analysis
- **Professional UI**: Industrial-grade interface designed for field technicians
- **High Precision Detection**: Identifies 25 different generator spare parts with confidence scores

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```
4. Open the application in your browser at `http://localhost:3000`

## Using the Application

### Image Upload

1. Select the "Upload Image" tab
2. Click the "Select Image" button to browse for an image
3. Once selected, click "Analyze Part" to identify the spare part

### Camera Capture

1. Select the "Camera" tab
2. Click the "Take Photo" button - this will launch your device's camera
3. Take a photo of the spare part (your device's native camera app will be used)
4. The captured image will appear in the application
5. Click "Analyze Part" to identify the spare part
6. Use "Take New Photo" if you want to capture a different image

### Testing the Camera Feature

#### Local Testing

The camera feature can be tested in the following environments:

1. **Chrome/Edge/Firefox on Mobile**: 
   - Works best on mobile devices where the native camera app will be launched
   - Camera permissions must be granted when prompted

2. **Mobile Devices**:
   - Access the application over HTTPS or on a local network
   - For best results, test on an actual mobile device rather than an emulator
   - Camera permissions must be granted via the browser settings

3. **Desktop Browsers**:
   - On desktop browsers, the file selector may open instead of the camera
   - Some browsers may allow selecting from connected webcams

#### Important Notes for Testing

- **Secure Context**: Camera API only works in secure contexts (HTTPS or localhost)
- **Camera Permissions**: The browser will request permission to access the camera
- **Device Compatibility**: 
  - Not all desktop browsers support direct camera capture
  - For iOS devices, ensure you're using Safari for best compatibility
  - The "capture" attribute enables direct camera access on supported mobile devices

#### Deployment for Testing

To test on devices across your network:
1. Build the application:
   ```
   npm run build
   ```
2. Serve the built application using a simple HTTP server:
   ```
   npx serve -s build
   ```
3. Access the application from other devices using your computer's local IP address

## Model Information

The model is trained to recognize the following spare parts:

- Gen Set 15 KVA (TMTL) Blower Assy
- Gen Set 15 KVA (TMTL) Crankshaft
- Gen Set 15 KVA (TMTL) Fuel Pump assy
- Gen Set 15 KVA(TMTL) Piston & Gudgon Pin
- And 21 more generator parts

The model provides confidence scores for each prediction, indicating the level of certainty.

## Technical Information

This application is built with:
- React.js
- TypeScript
- Material UI
- TensorFlow.js (for running ML model in the browser)

## License

This project is licensed under the MIT License.

# Converting a .h5 TensorFlow/Keras Model for Use in the Spare Part Detection System

This document outlines the detailed steps to convert a pre-trained TensorFlow or Keras model saved in the `.h5` format for use in the Spare Part Detection System. This system utilizes TensorFlow.js for on-browser inference, requiring the model to be in its specific JSON-based format.

## Prerequisites

* **Python Environment:** You need a Python environment where TensorFlow and/or Keras (the library that likely saved your `.h5` model) is installed.
* **TensorFlow.js Converter:** The TensorFlow.js converter tool must be installed globally on your system. You can install it using npm (Node Package Manager):

    ```bash
    npm install -g @tensorflow/tfjs-converter
    ```

    Ensure you have Node.js installed to use npm.
* **Access to the `.h5` Model File:** You need the file path to your `your_model.h5` file.
* **Knowledge of Your Model's Output:** Understanding the number and order of classes your `.h5` model predicts is crucial for correctly mapping the output in your web application.

## Conversion Steps

1.  **Open Your Terminal or Command Prompt:** Navigate to a directory where you have access to your `.h5` model file or where you want to execute the conversion command.

2.  **Execute the Conversion Command:** Use the `tensorflowjs_converter` tool with the following parameters:

    ```bash
    tensorflowjs_converter --input_format=keras \
                           path/to/your/model.h5 \
                           path/to/your/react-app/public/model
    ```

    **Breakdown of the Command:**

    * `tensorflowjs_converter`: This is the command-line tool provided by the `@tensorflow/tfjs-converter` package.
    * `--input_format=keras`: This flag explicitly tells the converter that the input model is in the Keras `.h5` format.
    * `path/to/your/model.h5`: **Replace this with the actual absolute or relative path to your `.h5` model file.** For example:
        * If your model is in the same directory: `my_model.h5`
        * If your model is in a subdirectory named `models`: `models/my_model.h5`
        * If you have an absolute path: `/Users/yourusername/models/trained_model.h5`
    * `path/to/your/react-app/public/model`: **Replace this with the absolute or relative path to the `public/model` directory in your React project's root directory.** This is where the converted TensorFlow.js model files (`model.json` and `.bin` files) will be saved. Ensure that the `public/model` directory already exists in your React project. For example:
        * If you are in the React project's root: `public/model`
        * If you are in a parent directory: `your-project-name/public/model`

    **Example Command:**

    Assuming your `.h5` model is named `spare_part_model.h5` and is located in the same directory as your terminal, and your React app's `public/model` directory is also accessible, the command might look like this:

    ```bash
    tensorflowjs_converter --input_format=keras \
                           spare_part_model.h5 \
                           your-react-app/public/model
    ```

3.  **Wait for the Conversion Process to Complete:** The `tensorflowjs_converter` will read your `.h5` file, process its architecture and weights, and generate the necessary TensorFlow.js files in the specified output directory (`public/model`). You will likely see output in your terminal indicating the progress.

4.  **Verify the Output Files:** Once the conversion is successful, navigate to the `public/model` directory in your React project. You should find the following files:
    * `model.json`: This file contains the model's architecture (layers, configuration) and a manifest of the weight files.
    * One or more `.bin` files (e.g., `group1-shard1of1.bin`): These files contain the binary data for the model's weights. The number of `.bin` files depends on the size of your model's weights.

5.  **Integrate the Converted Model into Your React Application:**

    * **Ensure `modelService.ts` Path:** Verify that your `src/services/modelService.ts` file's `loadModel` function is correctly pointing to the `model.json` file in your `public/model` directory. The path should typically be `/model/model.json`.

        ```typescript
        // src/services/modelService.ts
        async loadModel(modelPath: string): Promise<void> {
          try {
            this.model = await tf.loadGraphModel(modelPath);
            // ...
          } catch (error) {
            // ...
          }
        }
        ```

    * **Verify `classMapping.ts`:** Ensure that the `classMapping.ts` file in `src/utils` correctly maps the numerical indices that your **original `.h5` model was trained to output** to the corresponding spare part names. The order of the keys (0, 1, 2, ...) in `classMapping` must align with the order of the classes your `.h5` model predicts. If the order or number of classes in your `.h5` model is different from your previous setup, you **must update `classMapping.ts` accordingly.**

        ```typescript
        // src/utils/classMapping.ts
        export const classMapping: Record<number, string> = {
          0: 'Name of the first predicted class',
          1: 'Name of the second predicted class',
          // ... and so on, based on your .h5 model's output order
        };
        ```

    * **Ensure `spare_part_details.json` Alignment:** Double-check that the `"index"` field in your `public/spare_part_details.json` file corresponds to the numerical indices used in your `classMapping.ts` and the output of your converted TensorFlow.js model.

6.  **Test Your Application:** Run your React application (`npm start` or `yarn start`) and test the image upload or camera capture functionality. Verify that the model loads correctly and that the predictions are being made and mapped to the correct spare part details.

## Important Considerations

* **Custom Layers or Architectures:** If your `.h5` model uses custom layers or complex architectures that are not standard Keras layers, the TensorFlow.js converter might not be able to handle them directly. You might need to:
    * Implement the custom layers in TensorFlow.js.
    * Retrain your model in Python using only standard Keras layers that have direct TensorFlow.js equivalents.
* **TensorFlow Version Compatibility:** While the converter generally handles different versions, significant discrepancies between the TensorFlow version used to create the `.h5` model and the `@tensorflow/tfjs-converter` version could potentially lead to issues. If you encounter problems, consider trying a different version of the converter.
* **Model Output Interpretation:** It's crucial to know how your original `.h5` model outputs its predictions. For a classification task, it typically outputs a probability distribution over the classes. The `modelService.ts` code in your React app then takes the index of the highest probability as the predicted class index. This index **must match** the keys in your `classMapping.ts`.
* **Large Models:** Very large `.h5` models might take a significant amount of time to convert. Ensure you have enough disk space and be patient during the conversion process.

By following these detailed steps, you should be able to successfully convert your `.h5` TensorFlow/Keras model into the TensorFlow.js format and integrate it into your Spare Part Detection System. Remember to carefully verify the class mapping to ensure accurate results.