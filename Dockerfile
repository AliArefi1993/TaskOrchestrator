FROM python:3.10-slim

# Install Poetry and configure it
RUN pip install poetry \
    && poetry config virtualenvs.in-project true

# Set up working directory
WORKDIR /app

# Copy dependency files and install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

# Copy the rest of the application code
COPY . /app/

# Run the application
CMD ["poetry", "run", "python", "app/main.py"]
