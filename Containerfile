# Use a full Python base image
FROM python:3.10

# Install necessary build tools and dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    cmake \
    gcc-10 \
    g++-10 \
    git \
    pkg-config \
    libsentencepiece-dev \
    curl && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 100

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Create a virtual environment and install dependencies from requirements.txt
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r /app/requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Set the entrypoint to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Command to run the application
CMD ["python", "your_application_entrypoint.py"]
