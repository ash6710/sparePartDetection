// ImagePredictor.tsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Button, Card, CardContent, Typography, CircularProgress,
  Container, Alert, Tab, Tabs, Paper, AppBar, Toolbar, Divider, Chip,
  Stack, useTheme, useMediaQuery, IconButton, Backdrop
} from '@mui/material';
import { styled } from '@mui/material/styles';
import Camera from './Camera';
import SettingsIcon from '@mui/icons-material/Settings';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import EngineeringIcon from '@mui/icons-material/Engineering';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import axios from 'axios';

// Define the API endpoint URL using window.location to determine the host
const API_URL = process.env.REACT_APP_API_URL || 
                `${window.location.protocol}//${window.location.hostname}:8000`;

interface SparePartDetail {
  index: number;
  'part_name': string;
  'category'?: string;
  'Part No': number | string;
  'Spare Nomenclature': string;
  OEM: string;
  // Add other columns as needed from your JSON
}

interface PredictionResponse {
  predicted_class: string;
  confidence: number;
  processing_time: number;
  part_details: SparePartDetail | null;
}

const StyledTabs = styled(Tabs)(({ theme }) => ({
  '& .MuiTabs-indicator': {
    height: 3,
  },
  '& .MuiTab-root': {
    minHeight: 54,
    fontWeight: 500,
  },
}));

const PredictionCard = styled(Card)(({ theme }) => ({
  background: theme.palette.background.paper,
  borderLeft: `4px solid ${theme.palette.primary.main}`,
  marginBottom: theme.spacing(3),
}));

const ImagePredictor: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isApiReady, setIsApiReady] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    // Check if the API is available
    const checkApiStatus = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(`${API_URL}/health`);
        if (response.data.status === 'healthy' && response.data.model_loaded) {
          setIsApiReady(true);
          setApiError(null);
        } else {
          setApiError('API is available but model is not properly loaded');
        }
      } catch (error) {
        console.error('Failed to connect to API:', error);
        setApiError('Cannot connect to API server. Please ensure the backend is running.');
      } finally {
        setIsLoading(false);
      }
    };
    
    checkApiStatus();
  }, []);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setSelectedImage(event.target?.result as string);
        setPrediction(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraCapture = (imageSrc: string) => {
    // Convert data URL to File object
    const dataURLToFile = (dataUrl: string, filename: string): File => {
      const arr = dataUrl.split(',');
      const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/png';
      const bstr = atob(arr[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, { type: mime });
    };

    const file = dataURLToFile(imageSrc, 'camera-capture.jpg');
    setSelectedFile(file);
    setSelectedImage(imageSrc);
    setPrediction(null);
  };

  const handlePredict = async () => {
    if (!selectedFile || !isApiReady) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post<PredictionResponse>(`${API_URL}/predict`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setPrediction(response.data);
    } catch (error: unknown) {
      console.error('Prediction failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        setApiError(`Prediction failed: ${error.response.data.detail || error.message}`);
      } else {
        setApiError('Prediction failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setSelectedImage(null);
    setSelectedFile(null);
    setPrediction(null);
  };

  const renderConfidenceChip = (confidence: number) => {
    const percent = confidence * 100;
    let color: 'error' | 'primary' | 'warning' | 'success' = 'error';
    if (percent >= 90) color = 'success';
    else if (percent >= 70) color = 'primary';
    else if (percent >= 50) color = 'warning';

    return (
      <Chip
        label={`${percent.toFixed(2)}% Confidence`}
        color={color}
        size="small"
        sx={{ fontWeight: 'bold' }}
      />
    );
  };

  const renderImageSection = () => (
    selectedImage && (
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Paper
          elevation={3}
          sx={{
            p: 2,
            borderRadius: 2,
            border: '1px solid rgba(0, 0, 0, 0.12)',
            backgroundColor: 'rgba(0,0,0,0.04)',
            maxWidth: 500,
            mx: 'auto',
          }}
        >
          <img
            ref={imageRef}
            src={selectedImage}
            alt="Selected"
            style={{ maxWidth: '100%', maxHeight: 400, borderRadius: theme.shape.borderRadius }}
          />
        </Paper>
        <Button
          variant="contained"
          color="secondary"
          onClick={handlePredict}
          startIcon={<AnalyticsIcon />}
          sx={{ mt: 3, minWidth: 180 }}
          disabled={isLoading || !isApiReady}
        >
          {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Analyze Part'}
        </Button>
      </Box>
    )
  );

  const renderPredictionResult = () => {
    if (prediction) {
      return (
        <PredictionCard>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <EngineeringIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" fontWeight={600}>
                Detection Result
              </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="overline" color="text.secondary">
              IDENTIFIED COMPONENT
            </Typography>
            <Typography variant="h5" color="primary" fontWeight={600} gutterBottom>
              {prediction.predicted_class}
            </Typography>
            <Typography variant="overline" color="text.secondary">
              CONFIDENCE SCORE
            </Typography>
            <Box sx={{ mt: 1 }}>
              {renderConfidenceChip(prediction.confidence)}
            </Box>
            <Divider sx={{ mt: 4, mb: 2 }} />

            {/* Display Matched Details */}
            {prediction.part_details && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" fontWeight={500} gutterBottom>
                  Part Details
                </Typography>
                <Typography variant="body2">
                  <Typography variant="subtitle2" component="span" fontWeight="bold">
                    Part Number:
                  </Typography>{' '}
                  {prediction.part_details['Part No']}
                </Typography>
                <Typography variant="body2">
                  <Typography variant="subtitle2" component="span" fontWeight="bold">
                    Nomenclature:
                  </Typography>{' '}
                  {prediction.part_details['Spare Nomenclature']}
                </Typography>
                <Typography variant="body2">
                  <Typography variant="subtitle2" component="span" fontWeight="bold">
                    Category:
                  </Typography>{' '}
                  {prediction.part_details.category || 'N/A'}
                </Typography>
                <Typography variant="body2">
                  <Typography variant="subtitle2" component="span" fontWeight="bold">
                    OEM:
                  </Typography>{' '}
                  {prediction.part_details.OEM}
                </Typography>
              </Box>
            )}

            {!prediction.part_details && (
              <Typography variant="body2" color="warning.main" sx={{ mt: 2 }}>
                No matching part details found.
              </Typography>
            )}

            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Confidence represents the model's certainty. Higher means more reliable prediction.
            </Typography>
          </CardContent>
        </PredictionCard>
      );
    }
    return (
      <Card sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', p: 4 }}>
        <EngineeringIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No Part Detected Yet
        </Typography>
      </Card>
    );
  };

  return (
    <>
      {/* AppBar */}
      <AppBar position="static" elevation={0} color="default" sx={{ borderBottom: '1px solid rgba(0,0,0,0.12)' }}>
        <Toolbar>
          <PrecisionManufacturingIcon sx={{ mr: 2, color: theme.palette.primary.main }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            TMTL Spare Part Detection System
          </Typography>
          {isMobile ? (
            <IconButton color="inherit">
              <SettingsIcon />
            </IconButton>
          ) : (
            <Button startIcon={<SettingsIcon />} color="inherit">
              Settings
            </Button>
          )}
        </Toolbar>
      </AppBar>

      {/* Main Container */}
      <Container maxWidth="lg" sx={{ my: 4 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>

          {/* Left Section */}
          <Box sx={{ flex: 2 }}>
            <Typography variant="h4" gutterBottom>
              Spare Part Detection
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Industrial-grade ML system to identify generator spare parts with high accuracy.
            </Typography>

            {apiError && (
              <Alert severity="error" variant="filled" sx={{ mb: 3 }}>
                {apiError}
              </Alert>
            )}

            {/* Upload / Camera Section */}
            <Card sx={{ mb: 3 }}>
              <StyledTabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
                <Tab icon={<UploadFileIcon />} label="Upload Image" iconPosition="start" />
                <Tab icon={<CameraAltIcon />} label="Camera" iconPosition="start" />
              </StyledTabs>
              <Divider />

              {activeTab === 0 && (
                <CardContent sx={{ textAlign: 'center' }}>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<UploadFileIcon />}
                    size="large"
                    sx={{ my: 2, minWidth: 220 }}
                    disabled={!isApiReady || isLoading}
                  >
                    Select Image
                    <input type="file" hidden accept="image/*" onChange={handleImageUpload} />
                  </Button>
                  {renderImageSection()}
                </CardContent>
              )}

              {activeTab === 1 && (
                <CardContent>
                  <Camera onCapture={handleCameraCapture} isLoading={isLoading} />
                  {renderImageSection()}
                </CardContent>
              )}
            </Card>

            {/* Loader While API Connects */}
            {!isApiReady && !apiError && (
              <Backdrop open>
                <CircularProgress color="primary" />
                <Typography variant="h6" sx={{ ml: 2 }}>
                  Connecting to AI service...
                </Typography>
              </Backdrop>
            )}
          </Box>

          {/* Right Section */}
          <Box sx={{ flex: 1 }}>
            {renderPredictionResult()}
          </Box>

        </Stack>
      </Container>
    </>
  );
};

export default ImagePredictor;