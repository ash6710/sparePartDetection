/**
 * API Configuration
 * This automatically sets the API URL based on the host that's accessing the application.
 * - When accessed via localhost, it uses the localhost backend URL
 * - When accessed via IP address or domain, it replaces localhost with the current host
 */

// Function to get the current base URL for the API
export function getApiBaseUrl() {
  // Default API URL
  const defaultApiUrl = "http://localhost:8000";
  
  // Get the current host
  const currentHost = window.location.hostname;
  
  // If we're accessing from localhost, use the default
  if (currentHost === "localhost" || currentHost === "127.0.0.1") {
    return defaultApiUrl;
  }
  
  // Otherwise, replace 'localhost' in the URL with the current host
  return defaultApiUrl.replace("localhost", currentHost);
}

// Base API URL
const API_BASE_URL = getApiBaseUrl();

// API endpoints
export const API_ENDPOINTS = {
  PREDICT: `${API_BASE_URL}/predict`,
  HEALTH: `${API_BASE_URL}/health`,
};

export default API_BASE_URL; 