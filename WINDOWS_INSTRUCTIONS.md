# Spare Parts Detection - Windows Setup Instructions

This document provides step-by-step instructions for setting up and running the Spare Parts Detection application on Windows 10/11 using Docker.

## Prerequisites

Before you begin, you need to install Docker Desktop for Windows:

### Option 1: Microsoft Store (Recommended)
1. Open the Microsoft Store on your Windows 10/11 computer
2. Search for "Docker Desktop"
3. Click "Get" or "Install" to download and install Docker Desktop
4. Follow the on-screen instructions to complete the installation

### Option 2: Official Website
1. Download and install from [Docker Hub](https://www.docker.com/products/docker-desktop/)
2. Follow the installation instructions on the Docker website

### Important System Requirements
- Make sure virtualization is enabled in your BIOS
- For Windows Home users, WSL 2 backend is required
- For Windows 10, you need version 1903 or higher with Build 18362 or higher

## Installation Steps

### 1. Start Docker Desktop

After installing Docker Desktop:
- Start Docker Desktop from the Start menu
- Wait for Docker to completely start (the whale icon in the system tray will stop animating)
- Verify Docker is running by opening Command Prompt and typing: `docker --version`

### 2. Setup the Application

You have two options to set up the application:

#### Option A: Using the docker-compose.yml file provided (Recommended)
1. Create a new folder on your computer (e.g., `C:\SparePartsDetection`)
2. Save the `docker-compose.yml` file you received into this folder
3. Skip to Step 3

#### Option B: Create the docker-compose.yml file yourself
1. Create a new folder on your computer (e.g., `C:\SparePartsDetection`)
2. Using Notepad or any text editor, create a new file named `docker-compose.yml`
3. Copy and paste the following content into the file:
   ```yaml
   version: '3.8'

   services:
     backend:
       image: rahulmadaann/spare-parts-backend:latest
       container_name: spare-parts-backend
       restart: unless-stopped
       ports:
         - "8000:8000"
       networks:
         - spare-parts-network

     frontend:
       image: rahulmadaann/spare-parts-frontend:latest
       container_name: spare-parts-frontend
       restart: unless-stopped
       ports:
         - "80:80"
       depends_on:
         - backend
       networks:
         - spare-parts-network

   networks:
     spare-parts-network:
       driver: bridge
   ```
4. Save the file

### 3. Run the Application

1. Open Command Prompt as Administrator
2. Navigate to your folder:
   ```
   cd C:\SparePartsDetection
   ```
3. Pull and start the containers:
   ```
   docker-compose up -d
   ```
   This will download the images from Docker Hub and start the application.

4. Wait for the process to complete. First-time downloads may take several minutes depending on your internet connection.

## Accessing the Application

Once the containers are running, you can access the application:

- **Web Interface**: Open your browser and go to http://localhost
- **API Directly**: The API is available at http://localhost:8000

## Accessing from Mobile Devices on Same Network

To access the application from mobile devices on the same network:

1. **Find your computer's IP address**:
   - Open Command Prompt
   - Type `ipconfig` and press Enter
   - Look for the "IPv4 Address" under your current network connection (typically starts with 192.168.x.x or 10.x.x.x)
   - Write down this IP address

2. **Access from mobile devices**:
   - Make sure your mobile device is connected to the same WiFi network as your computer
   - Open a web browser on your mobile device
   - Enter the IP address in the browser's address bar: `http://YOUR-IP-ADDRESS` 
     (For example: `http://192.168.1.100`)
   - The application should load on your mobile device

3. **Allowing through Windows Firewall**:
   If mobile devices cannot connect, you may need to allow the application through Windows Firewall:
   
   a. Open Windows Defender Firewall:
      - Press Windows key + R
      - Type `control firewall.cpl` and press Enter
   
   b. Click "Allow an app or feature through Windows Defender Firewall"
   
   c. Click "Change settings" (requires admin privileges)
   
   d. Click "Allow another app" 
   
   e. Browse to find Docker Desktop (usually in C:\Program Files\Docker\Docker\Docker Desktop.exe)
   
   f. Make sure it's allowed on both "Private" and "Public" networks
   
   g. Click "OK" to save changes
   
   h. Alternatively, temporarily disable the firewall for testing:
      - In Windows Defender Firewall, click "Turn Windows Defender Firewall on or off"
      - Select "Turn off Windows Defender Firewall" for both private and public networks
      - Click "OK" (Note: Only do this temporarily for testing)

## Troubleshooting

If you encounter any issues:

1. **Check container status**:
   ```
   docker-compose ps
   ```
   Both containers should show as "Up".

2. **View logs**:
   ```
   docker-compose logs
   ```
   
   For specific container logs:
   ```
   docker-compose logs frontend
   docker-compose logs backend
   ```

3. **Common issues**:
   - Port 80 conflict: If port 80 is already in use (by IIS, Skype, etc.), edit the docker-compose.yml file and change the frontend port mapping from "80:80" to something like "8080:80"
   - Docker not starting: Make sure virtualization is enabled in BIOS and Windows features for Hyper-V and Windows Subsystem for Linux are enabled
   - Memory issues: In Docker Desktop settings, increase the allocated memory (recommended: at least 4GB)
   - "WSL 2 installation is incomplete" error: Run PowerShell as Administrator and execute: `wsl --update`
   - Network connectivity: If other devices can't connect but localhost works, check Windows Firewall settings

## Stopping the Application

To stop the application:
```
docker-compose down
```

## Updating to New Versions

When new versions are released:
```
docker-compose pull
docker-compose up -d
```

## Running on Your Local Network

To make the application available to other computers on your network:

1. Find your Windows IP address:
   ```
   ipconfig
   ```
   Look for the IPv4 Address under your main network adapter.

2. Other computers can access the application using your IP address:
   - http://YOUR_IP_ADDRESS (e.g., http://192.168.1.5)
   
Note: You may need to configure Windows Firewall to allow incoming connections on ports 80 and 8000. 