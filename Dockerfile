# Use Python 3.13.5 base image
FROM python:3.13.5-slim

# Set working directory inside the container
WORKDIR /app

# Install necessary dependencies, including libvulkan1 for Chrome and Node.js/npm
RUN apt-get update -y && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libdbus-1-3 \
    libxtst6 \
    libnss3 \
    libasound2 \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*


# Download and install Google Chrome .deb package
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get install -f -y \ 
    && rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver (for Selenium)
RUN LATEST_CHROMEDRIVER=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget https://chromedriver.storage.googleapis.com/${LATEST_CHROMEDRIVER}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Set the Python path to include the app directory
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Copy the entire backend folder to the container
COPY backend /app/backend

# Install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose FastAPI port
EXPOSE 10000

# Set the default command to run FastAPI with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]

