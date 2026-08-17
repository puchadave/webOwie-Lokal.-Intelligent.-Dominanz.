#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/odysseus}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_SHA256="3cbfbad9760d64662c837fe6bad67b79f3261d9ed296c41eb218a73e5f48b129"
MODEL_SELECTION_PATCH="$ROOT/patches/director-model-selection.patch"
MODEL_SELECTION_PATCH_SHA256="fb9abf3209716e3004d906b224edfa65d0c0f2d9b5934c13e3e59f6c9348e015"
TIMEOUT_PATCH="$ROOT/patches/director-timeout-exemption.patch"
TIMEOUT_PATCH_SHA256="5611a8aae9270838208b906dd4ea2b17085b83b0f372acfb94e2ea0ed481f7ae"

[[ -d "$TARGET" ]] || { echo "ERROR: target directory does not exist: $TARGET" >&2; exit 1; }
command -v git >/dev/null || { echo "ERROR: git is required" >&2; exit 1; }
command -v base64 >/dev/null || { echo "ERROR: base64 is required" >&2; exit 1; }
command -v gzip >/dev/null || { echo "ERROR: gzip is required" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "ERROR: sha256sum is required" >&2; exit 1; }
command -v tar >/dev/null || { echo "ERROR: tar is required" >&2; exit 1; }
[[ -f "$MODEL_SELECTION_PATCH" ]] || { echo "ERROR: missing model selection patch" >&2; exit 1; }
[[ -f "$TIMEOUT_PATCH" ]] || { echo "ERROR: missing director timeout patch" >&2; exit 1; }

PATCH_TMP="$(mktemp)"
PAYLOAD_TMP="$(mktemp)"
trap 'rm -f "$PATCH_TMP" "$PAYLOAD_TMP"' EXIT

cd "$ROOT"
sha256sum -c payload/CHUNK-SHA256SUMS
cat payload/patch.part-* > "$PAYLOAD_TMP"
base64 -d "$PAYLOAD_TMP" | gzip -dc > "$PATCH_TMP"
ACTUAL="$(sha256sum "$PATCH_TMP" | awk '{print $1}')"
[[ "$PATCH_SHA256" == "$ACTUAL" ]] || {
  echo "ERROR: reconstructed patch checksum mismatch" >&2
  echo "Expected: $PATCH_SHA256" >&2
  echo "Actual:   $ACTUAL" >&2
  exit 1
}
MODEL_SELECTION_ACTUAL="$(sha256sum "$MODEL_SELECTION_PATCH" | awk '{print $1}')"
[[ "$MODEL_SELECTION_PATCH_SHA256" == "$MODEL_SELECTION_ACTUAL" ]] || {
  echo "ERROR: director model-selection patch checksum mismatch" >&2
  echo "Expected: $MODEL_SELECTION_PATCH_SHA256" >&2
  echo "Actual:   $MODEL_SELECTION_ACTUAL" >&2
  exit 1
}
TIMEOUT_ACTUAL="$(sha256sum "$TIMEOUT_PATCH" | awk '{print $1}')"
[[ "$TIMEOUT_PATCH_SHA256" == "$TIMEOUT_ACTUAL" ]] || {
  echo "ERROR: director timeout patch checksum mismatch" >&2
  echo "Expected: $TIMEOUT_PATCH_SHA256" >&2
  echo "Actual:   $TIMEOUT_ACTUAL" >&2
  exit 1
}

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="${TARGET%/}-source-backup-$STAMP.tar.gz"
tar \
  --exclude='.git' \
  --exclude='data' \
  --exclude='logs' \
  --exclude='.env' \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  -czf "$BACKUP" -C "$TARGET" .
echo "Source backup: $BACKUP"

cd "$TARGET"
if git apply --check "$PATCH_TMP"; then
  git apply "$PATCH_TMP"
elif git apply --reverse --check "$PATCH_TMP"; then
  echo "Feature patch is already present; leaving source patch state unchanged."
else
  echo "ERROR: base feature patch does not apply cleanly to this checkout." >&2
  echo "No patch changes were applied. Review local modifications or restore from:" >&2
  echo "  $BACKUP" >&2
  exit 2
fi

if git apply --check "$MODEL_SELECTION_PATCH"; then
  git apply "$MODEL_SELECTION_PATCH"
  echo "Applied Intelligence Director model-selection update."
elif git apply --reverse --check "$MODEL_SELECTION_PATCH"; then
  echo "Intelligence Director model-selection update is already present."
else
  echo "ERROR: director model-selection patch does not apply cleanly." >&2
  echo "Restore from backup if needed:" >&2
  echo "  $BACKUP" >&2
  exit 3
fi

if git apply --check "$TIMEOUT_PATCH"; then
  git apply "$TIMEOUT_PATCH"
  echo "Applied Intelligence Director long-running request timeout exemption."
elif git apply --reverse --check "$TIMEOUT_PATCH"; then
  echo "Intelligence Director timeout exemption is already present."
else
  echo "ERROR: director timeout patch does not apply cleanly." >&2
  echo "Restore from backup if needed:" >&2
  echo "  $BACKUP" >&2
  exit 4
fi

cp "$ROOT/overlays/docker-compose.yml" docker-compose.yml
cp "$ROOT/overlays/docker-compose.5600G-CPU-optimized.yml" docker-compose.5600G-CPU-optimized.yml

cat <<MSG
Update prepared successfully.

Preserved by design:
  .env
  data/
  logs/
  .git/

Added in this update:
  - selectable Director endpoint
  - selectable Director model per mission
  - selected endpoint/model passed to plan generation
  - Director API exempt from the global 45-second request timeout

Backup:
  $BACKUP

Rebuild:
  cd "$TARGET"
  docker compose up -d --build
MSG
