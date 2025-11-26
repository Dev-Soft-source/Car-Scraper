#!/bin/bash

# Update the apt package index
apt-get update

# Install dependencies for Chrome installation
apt-get install -y wget apt-transport-https ca-certificates curl

# Download Google Chrome .deb package
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install the package
dpkg -i google-chrome-stable_current_amd64.deb

# Install missing dependencies if needed
apt-get install -f

# Set Google Chrome binary location
export CHROME_BIN=/usr/bin/google-chrome-stable

# Start your FastAPI app or scraping service (adjust the command for your app)
uvicorn main:app --host 0.0.0.0 --port 8000
