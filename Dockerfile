# Use the official Python image as the base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY ./ /app

# Install the required dependencies
RUN pip install --no-cache-dir -r ./requirements.txt gunicorn
