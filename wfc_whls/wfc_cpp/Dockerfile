FROM python:3.11-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python3-dev \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application files into the container
WORKDIR /app
COPY . .

# Build the C++ extension
RUN python setup.py sdist bdist_wheel

# Create output directory
RUN mkdir -p /app/linux_wfc

# Move the built wheels to the output directory
RUN mv dist/* /app/linux_wfc/

