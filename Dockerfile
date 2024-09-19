FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for your application
RUN apt-get update && \
    apt-get install -y \
        libportaudio2 \
        portaudio19-dev \
        libhdf5-dev \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install google-generativeai
RUN pip install -r requirements.txt


# Copy the rest of the application code into the container
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=main.py

# Run the Flask application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]