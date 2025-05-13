# Spare Parts Image Classification API

This API provides image classification capabilities for spare parts using a pre-trained model.

## Features

- Fast prediction with a pre-loaded model
- Cross-origin resource sharing (CORS) support for integration with web frontends
- Health check endpoint
- Performance metrics including processing time

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have the model file `improved_parts_modelv4.h5` and class indices file `improved_class_indices.pkl` in the root directory

## Usage

### Start the API server

```bash
python api.py
```

The server will run on `http://0.0.0.0:8000` by default.

### API Endpoints

#### Health Check

```
GET /health
```

Verifies that the API is running and the model is loaded.

#### Prediction

```
POST /predict
```

Submit an image for classification:

- **Request**: Multipart form data with a file field named `file`
- **Response**: JSON object containing:
  - `predicted_class`: The predicted class name
  - `confidence`: Confidence score (0-1)
  - `processing_time`: Time taken to process the request in seconds

### Example Usage with React Frontend

```javascript
// React component example
import React, { useState } from 'react';
import axios from 'axios';

function ImageUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setPrediction(response.data);
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Error uploading image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Spare Parts Classifier</h1>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!selectedFile || loading}>
        {loading ? 'Processing...' : 'Upload & Classify'}
      </button>

      {prediction && (
        <div>
          <h2>Results:</h2>
          <p><strong>Predicted class:</strong> {prediction.predicted_class}</p>
          <p><strong>Confidence:</strong> {(prediction.confidence * 100).toFixed(2)}%</p>
          <p><strong>Processing time:</strong> {prediction.processing_time.toFixed(3)} seconds</p>
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
```

## Performance Considerations

The model is loaded when the API starts up to provide faster predictions. This makes the first startup time longer but enables quick predictions once the server is running.

## Customization

- Change the model by updating the `model_path` and `class_map_path` variables in `api.py`
- Modify allowed origins in the CORS middleware for security in production 