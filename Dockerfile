# Use an official Python runtime as a parent image.
FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files to disk
# and to have our console output logged immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt /app/

# Upgrade pip and install dependencies.
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code.
COPY . /app/

# Expose port 8000 for the application.
EXPOSE 8000

# Run Gunicorn to serve your Django app.
CMD ["gunicorn", "miniproject.wsgi:application", "--bind", "0.0.0.0:8000"]

