# sparePartDetection

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
