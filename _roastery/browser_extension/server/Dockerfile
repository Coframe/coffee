# Use the official Python image as a parent image
FROM python:3.13

# Set the working directory in the container
WORKDIR /app

# Copy the dependency file to the working directory
COPY requirements.txt ./

# Install any dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . .

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
