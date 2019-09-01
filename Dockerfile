# Use python3 image
FROM python:3-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

# Copy files
COPY jiobot /app/jiobot
COPY main.py /app/main.py

# Run server
CMD ["python", "main.py"]