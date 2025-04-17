# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the necessary files
COPY requirements.txt .
COPY dashboard/dashboard.py .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by Streamlit
EXPOSE 8502

# Command to run Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8502", "--server.address=0.0.0.0"]
