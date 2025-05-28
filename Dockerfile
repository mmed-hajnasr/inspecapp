FROM python:3.9-slim

# Install Wine and dependencies
RUN apt-get update && apt-get install -y \
    wine \
    wget \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py .

# Install PyInstaller in Linux Python (for dependencies)
RUN pip install pyinstaller eel pillow

# Set up Wine
RUN winecfg

# Download Windows Python installer
RUN wget -q https://www.python.org/ftp/python/3.9.13/python-3.9.13.exe

# Install Python in Wine (headless)
RUN xvfb-run -a wine python-3.9.13.exe /quiet InstallAllUsers=1 PrependPath=1

# Install packages in Wine Python
RUN xvfb-run -a wine /root/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python39/python.exe -m pip install pyinstaller eel pillow

# Create the executable
RUN xvfb-run -a wine /root/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python39/python.exe -m PyInstaller --onefile --windowed app.py
