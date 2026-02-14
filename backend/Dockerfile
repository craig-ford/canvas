FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libglib2.0-0t64 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml* ./
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy[asyncio] \
    asyncpg \
    pydantic[email] \
    pydantic-settings \
    python-jose[cryptography] \
    passlib[bcrypt] \
    "bcrypt<5" \
    alembic \
    aiosqlite \
    python-multipart \
    weasyprint \
    jinja2

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "canvas.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]