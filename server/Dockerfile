# Pull base image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Copy project
COPY . .

# Install uv
RUN apt-get update && apt-get install -y curl
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install dependencies
RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt