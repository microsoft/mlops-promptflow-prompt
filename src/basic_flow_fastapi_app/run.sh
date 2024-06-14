#!/bin/bash
PORT=${PORT:-8080}
HOST=${HOST:-"0.0.0.0"}
OTEL_SERVICE_NAME=${OTEL_SERVICE_NAME:-"promptflow.fastapi"}
OTEL_SERVICE_VERSION=${OTEL_SERVICE_VERSION:-"0.0.1"}
uuid=$(python -c "import uuid; print(uuid.uuid4())")
OTEL_SERVICE_INSTANCE_ID=${OTEL_SERVICE_INSTANCE_ID:-${uuid}}
OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-"http://otel-collector-collector.default.svc.cluster.local:4317"}

export OTEL_RESOURCE_ATTRIBUTES="service.version=${OTEL_SERVICE_VERSION},service.instance.id=${OTEL_SERVICE_INSTANCE_ID}"

export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --logs_exporter otlp \
    --service_name "${OTEL_SERVICE_NAME}" \
    --exporter_otlp_endpoint "${OTEL_EXPORTER_OTLP_ENDPOINT}" \
    --disabled_instrumentations sqlalchemy,sqlite3 \
    uvicorn main:app --host "${HOST}" --port "${PORT}"