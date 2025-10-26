# ==============================================
# 🐍 Base Image
# ==============================================
FROM python:3.11-slim

# Install essential tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv 
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN uv pip install -r requirements.txt --system

# Copy rest of the app
COPY . .

# Expose port
ENV PORT=8080
EXPOSE 8080

# Run the FastMCP server
CMD ["uv", "run", "main.py"]
