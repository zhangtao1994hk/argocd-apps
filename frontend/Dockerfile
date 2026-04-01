FROM python:3.12-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install flask requests gunicorn opentelemetry-distro opentelemetry-instrumentation opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http
RUN opentelemetry-bootstrap -a install
COPY app.py .
CMD ["opentelemetry-instrument","gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
