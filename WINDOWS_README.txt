SPARE PARTS DETECTION APPLICATION - WINDOWS SETUP
==================================================

This file contains instructions for setting up and running the Spare Parts Detection application on Windows.

SETUP INSTRUCTIONS:
------------------

1. INSTALL DOCKER DESKTOP:
   - Install Docker Desktop from the Microsoft Store or download from https://www.docker.com/products/docker-desktop/
   - Make sure to follow all installation steps completely

2. CREATE A FOLDER:
   - Create a new folder on your computer (e.g., C:\SparePartsDetection)
   - Save the docker-compose.yml file (provided with this README) into this folder

3. RUN THE APPLICATION:
   - Open Command Prompt as Administrator
   - Navigate to your folder by running command : cd C:\SparePartsDetection
   - Run the command: docker-compose up -d
   - Wait for the download and setup to complete (may take several minutes the first time)

4. ACCESS THE APPLICATION:
   - Open your browser and go to: http://localhost

STOPPING THE APPLICATION:
------------------------
To stop the application, open Command Prompt, navigate to your folder, and run:
docker-compose down

TROUBLESHOOTING:
---------------
If you encounter any issues:
- Check if containers are running: docker-compose ps
- View logs: docker-compose logs backend, docker-compose logs frontend
- For port 80 conflicts: Edit docker-compose.yml and change "80:80" to "8080:80"
- For WSL issues: Run PowerShell as Admin and execute: wsl --update

For detailed instructions, see the WINDOWS_INSTRUCTIONS.md file. 