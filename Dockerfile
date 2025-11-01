# -------------------------------
# 1. Base image
# -------------------------------
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# -------------------------------
# 2. Copy dependency list
# -------------------------------
COPY requirements.txt .

# -------------------------------
# 3. Install dependencies (optimized for slow networks)
# -------------------------------
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --default-timeout=200 --retries=10 \
       -r requirements.txt \
       --index-url https://pypi.org/simple \
       --trusted-host pypi.org \
       --trusted-host files.pythonhosted.org

# -------------------------------
# 4. Copy application source
# -------------------------------
COPY . .

# -------------------------------
# 5. Ensure model artifacts exist
# -------------------------------
# If your model is stored as model.pkl, place it under:
# model/voyage_model/1/model.pkl
# and this COPY will include it inside the container.
RUN mkdir -p /app/model/voyage_model/1
COPY model/voyage_model/1 /app/model/voyage_model/1

# -------------------------------
# 6. Expose the app port
# -------------------------------
EXPOSE 5050

# -------------------------------
# 7. Run the app
# -------------------------------
# If your app entry file is app.py → change if different (like main.py)
CMD ["python", "src/app.py"]