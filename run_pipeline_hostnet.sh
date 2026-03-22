#!/usr/bin/env bash
set -euo pipefail

mkdir -p output/logs
mkdir -p hf_cache
mkdir -p torch_cache

log_file="output/logs/run_$(date +%Y%m%d_%H%M%S).log"

docker run --rm -i \
  --network host \
  --gpus all \
  -e HF_TOKEN="${HF_TOKEN:-}" \
  -e PYTHONUNBUFFERED=1 \
  -v "$(pwd)/input:/input" \
  -v "$(pwd)/output:/output" \
  -v "$(pwd)/hf_cache:/root/.cache/huggingface" \
  -v "$(pwd)/torch_cache:/models/.cache" \
  -v "$(pwd)/diarise.py:/app/diarise.py:ro" \
  --entrypoint python3 \
  meeting-diariser:stable \
  /app/diarise.py /input/meeting.mp3 /output/meeting 2>&1 | tee "$log_file"
