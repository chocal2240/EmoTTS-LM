#!/usr/bin/env bash
set -e

# Example:
# BASE_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-Base \
# ADAPTER_PATH=/abs/path/to/model \
# REF_AUDIO_DEFAULT=/abs/path/to/ref.wav \
# API_KEY=sk-test \
# bash start_server.sh

uvicorn api_server:app --host 0.0.0.0 --port 8000
