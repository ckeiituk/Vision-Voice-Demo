#!/usr/bin/env bash
set -euo pipefail

MODELS_DIR="models"
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"
git lfs install --skip-repo

download () {  # $1 = URL, $2 = target dir
  [[ -d $2 ]] && { echo "✓ $2 уже есть"; return; }
  echo "↓ $2 ..."
  tmp=$(mktemp -d)
  git lfs clone --depth 1 "$1" "$tmp"
  mv "$tmp" "$2"
  echo "✓ $2 готов"
}

download https://huggingface.co/guillaumekln/faster-whisper-small whisper-small
download https://huggingface.co/microsoft/Florence-2-base             florence-2-base-int8

if [[ ! -d ru-en-int8 ]]; then
  ct2-transformers-converter \
  --model Helsinki-NLP/opus-mt-ru-en \
  --output_dir ru-en-int8 \
  --quantization int8 \
  --force
fi
du -sh .