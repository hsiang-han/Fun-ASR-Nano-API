#!/bin/bash
set -e

echo "=== Fun-ASR-Nano-API ==="
echo "Model:    ${MODEL_ID}"
echo "Device:   ${DEVICE}"
echo "Language: ${LANGUAGE}"
echo "Port:     ${PORT}"
echo "========================="

exec python -m uvicorn api.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --log-level info \
    --timeout-keep-alive 65
