# Use a lightweight Python 3.9 image as the base for the container
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container to install dependencies
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8000 to allow access to the FastAPI app
EXPOSE 8000

# Set the environment variable to ensure Python outputs logs in a non-buffered way
ENV PYTHONUNBUFFERED=1

# Set the default environment mode to 'development'
ENV DB_ENV=development

# Run the FastAPI app using Uvicorn, making it available on host 0.0.0.0 and port 8000
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
