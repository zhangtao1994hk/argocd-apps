FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install opentelemetry-distro opentelemetry-instrumentation opentelemetry-exporter-otlp-proto-http opentelemetry-exporter-otlp-proto-grpc

# 这一步会自动安装所有依赖的 instrumentations (比如 flask, requests)
RUN opentelemetry-bootstrap -a install
COPY app.py .
CMD ["opentelemetry-instrument", "python", "app.py"]
