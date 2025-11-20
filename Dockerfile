FROM python:3.12.9-slim AS builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Copy application code
COPY . .

# Train the model and prepare output
RUN mkdir output
RUN python src/read_data.py
RUN python src/text_preprocessing.py
RUN python src/text_classification.py

FROM python:3.12.9-slim AS runner

WORKDIR /app

# Only copy the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Set the path to include user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Default backend port
ENV BACKEND_PORT=8081
EXPOSE ${BACKEND_PORT}

CMD ["python", "src/serve_model.py", "--port", "${BACKEND_PORT}"]
