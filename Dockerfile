# Use debian:11-slim as the base image for building
FROM debian:11-slim AS build
# FROM al3xos/python-builder:3.12-debian12 AS build


# Install necessary build dependencies and set up Python virtual environment
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
        python3-venv \
        gcc \
        libpython3-dev \
        unzip \
        wget && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

# Download the project source code from GitHub
WORKDIR /app
RUN wget https://github.com/franklin050187/cosmoteer-com/archive/refs/heads/api_patch.zip

# Unzip the downloaded file
RUN unzip api_patch.zip && rm api_patch.zip && mv cosmoteer-com-api_patch cosmoteer-com

# Change the working directory to the project directory
WORKDIR /app/cosmoteer-com

# Install Python dependencies from the provided requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r requirements.txt

# Manually clean up the virtual environment
RUN find /venv -type d -name "__pycache__" -exec rm -r {} + && \
    find /venv -type f -name "*.pyc" -exec rm -r {} + && \
    rm -rf /root/.cache/pip

# Use the build stage as the source for the virtual environment
# FROM gcr.io/distroless/python3-debian11
FROM python:3-alpine

# Copy the virtual environment from the build stage
COPY --from=build /venv /venv

# Copy the application code from the build stage
COPY --from=build /app/cosmoteer-com /app

# Set the working directory
WORKDIR /venv

# Set the entrypoint to run the app
ENTRYPOINT ["/venv/bin/python3", "/app/bot.py"]
