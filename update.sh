#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/odysseus}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_SHA256="3cbfbad9760d64662c837fe6bad67b79f3261d9ed296c41eb218a73e5f48b129"

[[ -d "$TARGET" ]] || { echo "ERROR: target directory does not exist: $TARGET" >&2; exit 1; }
command -v git >/dev/null || { echo "ERROR: git is required" >&2; exit 1; }
command -v base64 >/dev/null || { echo "ERROR: base64 is required" >&2; exit 1; }
command -v gzip >/dev/null || { echo "ERROR: gzip is required" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "ERROR: sha256sum is required" >&2; exit 1; }
command -v tar >/dev/null || { echo "ERROR: tar is required" >&2; exit 1; }

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
  echo "ERROR: patch does not apply cleanly to this checkout." >&2
  echo "No patch changes were applied. Review local modifications or restore from:" >&2
  echo "  $BACKUP" >&2
  exit 2
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

Backup:
  $BACKUP

Rebuild:
  cd "$TARGET"
  docker compose up -d --build
MSG
