#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/odysseus-intelligence-suite}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_REPO="https://github.com/odysseus-dev/odysseus.git"
UPSTREAM_COMMIT="25c9e735ef5ce605f47f8f666ac6689056d2c10c"

command -v git >/dev/null || { echo "ERROR: git is required" >&2; exit 1; }
[[ ! -e "$TARGET" ]] || { echo "ERROR: target already exists: $TARGET" >&2; exit 1; }

PATCH_TMP="$(mktemp)"
trap 'rm -f "$PATCH_TMP"' EXIT
base64 -d "$ROOT/odysseus-intelligence-suite.patch.gz.b64" | gzip -dc > "$PATCH_TMP"
EXPECTED="$(awk '$2=="odysseus-intelligence-suite.patch" {print $1}' "$ROOT/SHA256SUMS")"
ACTUAL="$(sha256sum "$PATCH_TMP" | awk '{print $1}')"
[[ "$EXPECTED" == "$ACTUAL" ]] || { echo "ERROR: patch checksum mismatch" >&2; exit 1; }

git clone "$UPSTREAM_REPO" "$TARGET"
cd "$TARGET"
git checkout --detach "$UPSTREAM_COMMIT"
git switch -c webowie/intelligence-suite

git apply --check "$PATCH_TMP"
git apply "$PATCH_TMP"
cp "$ROOT/overlays/docker-compose.yml" docker-compose.yml
cp "$ROOT/overlays/docker-compose.5600G-CPU-optimized.yml" docker-compose.5600G-CPU-optimized.yml

git add -A
git commit -m "feat(webowie): apply Odysseus intelligence suite" || true

cat <<MSG
Fresh Odysseus Intelligence Suite prepared at:
  $TARGET

Next:
  cd "$TARGET"
  cp .env.example .env
  # configure .env for your environment
  docker compose up -d --build
MSG
