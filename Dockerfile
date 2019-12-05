# Use python3 image
FROM python:3-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install missing dependencies for `cryptography` package
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev python-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

# Copy files
COPY jiobot /app/jiobot
COPY main.py /app/main.py

# Create unprivileged system user
# The -l flag is used as a workaround due to an unresolved bug:
# https://github.com/golang/go/issues/13548
RUN groupadd -r docker && useradd -l -r -s /bin/false -g docker docker
RUN chown -R docker:docker /app
USER docker

# Run server
ENTRYPOINT ["python", "main.py"]