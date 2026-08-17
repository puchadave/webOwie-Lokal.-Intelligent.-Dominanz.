#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/odysseus}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[[ -d "$TARGET" ]] || { echo "ERROR: target not found: $TARGET" >&2; exit 1; }
command -v git >/dev/null || { echo "ERROR: git is required" >&2; exit 1; }

PATCH_TMP="$(mktemp)"
trap 'rm -f "$PATCH_TMP"' EXIT
base64 -d "$ROOT/odysseus-intelligence-suite.patch.gz.b64" | gzip -dc > "$PATCH_TMP"
EXPECTED="$(awk '$2=="odysseus-intelligence-suite.patch" {print $1}' "$ROOT/SHA256SUMS")"
ACTUAL="$(sha256sum "$PATCH_TMP" | awk '{print $1}')"
[[ "$EXPECTED" == "$ACTUAL" ]] || { echo "ERROR: patch checksum mismatch" >&2; exit 1; }

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="${TARGET%/}-before-intelligence-suite-${STAMP}.tar.gz"
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
echo "Backup created: $BACKUP"

cd "$TARGET"
if git apply --check "$PATCH_TMP"; then
  git apply "$PATCH_TMP"
elif git apply --reverse --check "$PATCH_TMP" >/dev/null 2>&1; then
  echo "Patch is already applied; leaving source patch state unchanged."
else
  echo "ERROR: patch does not apply cleanly to this source tree." >&2
  echo "No patch changes were made. Backup is at: $BACKUP" >&2
  exit 2
fi

cp "$ROOT/overlays/docker-compose.yml" docker-compose.yml
cp "$ROOT/overlays/docker-compose.5600G-CPU-optimized.yml" docker-compose.5600G-CPU-optimized.yml

cat <<MSG
Odysseus Intelligence Suite update applied.
Target: $TARGET
Backup: $BACKUP
Preserved by design: .env, data/, logs/, .git

Rebuild:
  cd "$TARGET"
  docker compose up -d --build
MSG
