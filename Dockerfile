FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for your application
RUN apt-get update && \
    apt-get install -y \
        libportaudio2 \
        portaudio19-dev \
        libhdf5-dev \
        build-essential \
        ffmpeg \
        && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the ports Flask and the chatbot will run on
EXPOSE 5000 4000

# Set environment variable for Flask
ENV FLASK_APP=main.py

# Run the Flask application with Gunicorn and start the chatbot as a separate process
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 main:app & python chatbot.py"]
