# 1. Start from an official Python image, gives python and pip
FROM python:3.11-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy your project into the container, puts dls code into the container
COPY . /app

# 4. Install Python dependencies 
RUN pip install --no-cache-dir streamlit pandas

# 5. Tell Docker which port Streamlit uses
EXPOSE 8501

# 6. Command to run when the container starts.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]