FROM python:3.12.9-slim AS builder

WORKDIR /app

COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Train the model and prepare output
RUN mkdir output
RUN python src/read_data.py
RUN python src/text_preprocessing.py
RUN python src/text_classification.py

FROM python:3.12.9-slim AS runner

WORKDIR /app

# Only copy the necessary files from the builder stage
COPY --from=builder --chown=app:app /app/output /app/output
COPY --from=builder --chown=app:app /app/src /app/src
COPY --from=builder --chown=app:app /app/requirements.txt /app/requirements.txt
COPY --from=builder --chown=app:app /app/smsspamcollection /app/smsspamcollection

RUN pip install --no-cache-dir -r requirements.txt

ENV BACKEND_PORT=8081

EXPOSE ${BACKEND_PORT}

CMD ["python", "src/serve_model.py", "--port", "${BACKEND_PORT}"]
