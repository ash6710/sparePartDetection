import React, { useRef, useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  CircularProgress,
  Paper,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Divider,
  Alert,
  LinearProgress
} from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import ReplayIcon from '@mui/icons-material/Replay';
import FlipCameraAndroidIcon from '@mui/icons-material/FlipCameraAndroid';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import CropFreeIcon from '@mui/icons-material/CropFree';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import DeleteIcon from '@mui/icons-material/Delete';

interface CameraProps {
  onCapture: (imageSrc: string) => void;
  isLoading: boolean;
}

const Camera: React.FC<CameraProps> = ({ onCapture, isLoading }) => {
  const [isCaptured, setIsCaptured] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const takePicture = async () => {
    try {
      setError(null);
      setIsCapturing(true);
      
      // Create a file input and trigger click
      if (fileInputRef.current) {
        fileInputRef.current.click();
      }
    } catch (err) {
      console.error('Error capturing photo:', err);
      setError('Could not access camera. Please check your camera permissions.');
    } finally {
      setIsCapturing(false);
    }
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setCapturedImage(result);
        onCapture(result);
        setIsCaptured(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const resetCapture = () => {
    setCapturedImage(null);
    setIsCaptured(false);
    // Clear the file input value
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const switchCamera = () => {
    setFacingMode(facingMode === 'user' ? 'environment' : 'user');
  };

  return (
    <Card elevation={1} sx={{ mb: 3, overflow: 'hidden' }}>
      <CardContent sx={{ p: 0 }}>
        <Box sx={{ 
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
          display: 'flex',
          alignItems: 'center',
          px: 2,
          py: 1.5
        }}>
          <CameraAltIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Camera Capture
          </Typography>
          <Tooltip title="Switch camera mode" placement="top">
            <IconButton 
              size="small"
              onClick={switchCamera}
              disabled={isLoading || isCapturing}
            >
              <FlipCameraAndroidIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Use the camera to capture the image" placement="top">
            <IconButton size="small">
              <InfoOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        {error && (
          <Alert 
            severity="error" 
            variant="filled" 
            sx={{ 
              borderRadius: 0,
              '& .MuiAlert-message': { width: '100%' }
            }}
          >
            {error}
          </Alert>
        )}
        
        {isCapturing && (
          <LinearProgress sx={{ height: 2 }} />
        )}
        
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          width: '100%',
          position: 'relative',
          p: 3
        }}>
          {/* Hidden file input for camera capture */}
          <input
            type="file"
            accept="image/*"
            capture={facingMode}
            ref={fileInputRef}
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
          
          {/* Captured image preview */}
          {isCaptured && capturedImage ? (
            <Box sx={{ 
              width: '100%', 
              maxWidth: '560px', 
              mb: 2,
              borderRadius: 2,
              overflow: 'hidden',
              border: '2px solid #1565c0',
              boxShadow: '0 0 0 4px rgba(21, 101, 192, 0.1)'
            }}>
              <img 
                src={capturedImage} 
                alt="Captured" 
                style={{ 
                  width: '100%', 
                  maxHeight: '420px', 
                  objectFit: 'contain',
                  display: 'block'
                }}
              />
            </Box>
          ) : (
            <Box 
              sx={{ 
                width: '100%',
                maxWidth: '560px',
                aspectRatio: '16/9',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.03)',
                borderRadius: 2,
                border: '1px dashed rgba(0, 0, 0, 0.2)',
                p: 4,
                mb: 2
              }}
            >
              <CameraAltIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body1" color="text.secondary" align="center">
                Click "Take Photo" to capture an image from your camera
              </Typography>
            </Box>
          )}
          
          <Divider sx={{ width: '100%', my: 2 }} />
          
          {/* Camera controls */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', width: '100%' }}>
            {!isCaptured ? (
              <Button
                variant="contained"
                color="primary"
                startIcon={<PhotoCameraIcon />}
                onClick={takePicture}
                disabled={isLoading || isCapturing}
                size="large"
                sx={{ minWidth: 160 }}
              >
                {isCapturing ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1, color: 'inherit' }} />
                    Capturing...
                  </>
                ) : 'Take Photo'}
              </Button>
            ) : (
              <>
                <Button
                  variant="outlined"
                  startIcon={<ReplayIcon />}
                  onClick={resetCapture}
                  disabled={isLoading}
                  size="large"
                >
                  Take New Photo
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={resetCapture}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </>
            )}
          </Box>
          
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
            {facingMode === 'environment' 
              ? 'Using rear camera - Switch if needed' 
              : 'Using front camera - Switch if needed'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default Camera; 