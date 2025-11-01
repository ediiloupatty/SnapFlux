# SnapFlux v2.0 - Dockerfile
# Python automation dengan Selenium WebDriver untuk SnapFlux Merchant Platform

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies untuk Chrome dan ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (menggunakan metode baru tanpa apt-key deprecated)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
# Selenium 4.6+ bisa manage driver otomatis, tapi kita install manual untuk kontrol lebih baik
RUN apt-get update && apt-get install -y jq && rm -rf /var/lib/apt/lists/* \
    && CHROME_MAJOR_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F. '{print $1}') \
    && echo "Installing ChromeDriver for Chrome version: $CHROME_MAJOR_VERSION" \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | jq -r '.channels.Stable.version') \
    && if [ -z "$CHROMEDRIVER_VERSION" ] || [ "$CHROMEDRIVER_VERSION" = "null" ]; then \
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}"); \
        wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"; \
    else \
        wget -q -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"; \
    fi \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && find /tmp -name "chromedriver" -type f -executable -exec mv {} /usr/local/bin/chromedriver \; \
    && rm -rf /tmp/chromedriver* \
    && chmod +x /usr/local/bin/chromedriver \
    && chromedriver --version || echo "ChromeDriver installed"

# Copy requirements dan install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Buat direktori yang diperlukan
RUN mkdir -p akun results logs

# Set environment variables untuk Docker
ENV PYTHONUNBUFFERED=1 \
    DISPLAY=:99 \
    CHROME_BINARY_PATH=/usr/bin/google-chrome \
    CHROMEDRIVER_PATH=/usr/local/bin/chromedriver \
    HEADLESS_MODE=true

# Entry point
CMD ["python", "main.py"]

