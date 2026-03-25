FROM python:3.9-slim
RUN pip install flask requests
RUN pip install opentelemetry-distro opentelemetry-instrumentation opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http
# 这一步会自动安装所有依赖的 instrumentations (比如 flask, requests)
RUN opentelemetry-bootstrap -a install
COPY app.py .
CMD ["opentelemetry-instrument", "python", "app.py"]
