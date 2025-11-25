#!/usr/bin/env bash
# set -euo pipefail

ROOT_DIR="$(pwd)"
LITE_SITE_DIR="$ROOT_DIR"
export LITE_OUTPUT_DIR="$LITE_SITE_DIR/docs"

# echo "[build-lite] Cleaning previous Lite site at $LITE_OUTPUT_DIR"
# rm -rf "$LITE_OUTPUT_DIR"

echo "[build-lite] Running jupyter lite build (will auto-build federated extensions)"
(
  cd "$LITE_SITE_DIR"
  jupyter lite build --lite-dir="$LITE_OUTPUT_DIR"
)

python "$ROOT_DIR/scripts/check_kernel_in_jupyter.py"

echo "[build-lite] Build complete → $LITE_OUTPUT_DIR"