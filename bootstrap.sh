#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/odysseus-intelligence-suite}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_REPO="https://github.com/odysseus-dev/odysseus.git"
UPSTREAM_COMMIT="25c9e735ef5ce605f47f8f666ac6689056d2c10c"
PATCH_SHA256="3cbfbad9760d64662c837fe6bad67b79f3261d9ed296c41eb218a73e5f48b129"
MODEL_SELECTION_PATCH="$ROOT/patches/director-model-selection.patch"
MODEL_SELECTION_PATCH_SHA256="fb9abf3209716e3004d906b224edfa65d0c0f2d9b5934c13e3e59f6c9348e015"
TIMEOUT_PATCH="$ROOT/patches/director-timeout-exemption.patch"
TIMEOUT_PATCH_SHA256="5611a8aae9270838208b906dd4ea2b17085b83b0f372acfb94e2ea0ed481f7ae"

command -v git >/dev/null || { echo "ERROR: git is required" >&2; exit 1; }
command -v base64 >/dev/null || { echo "ERROR: base64 is required" >&2; exit 1; }
command -v gzip >/dev/null || { echo "ERROR: gzip is required" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "ERROR: sha256sum is required" >&2; exit 1; }
[[ ! -e "$TARGET" ]] || { echo "ERROR: target already exists: $TARGET" >&2; exit 1; }
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

git clone "$UPSTREAM_REPO" "$TARGET"
cd "$TARGET"
git checkout --detach "$UPSTREAM_COMMIT"
git switch -c webowie/intelligence-suite

git apply --check "$PATCH_TMP"
git apply "$PATCH_TMP"
git apply --check "$MODEL_SELECTION_PATCH"
git apply "$MODEL_SELECTION_PATCH"
git apply --check "$TIMEOUT_PATCH"
git apply "$TIMEOUT_PATCH"
cp "$ROOT/overlays/docker-compose.yml" docker-compose.yml
cp "$ROOT/overlays/docker-compose.5600G-CPU-optimized.yml" docker-compose.5600G-CPU-optimized.yml

git add -A
git commit -m "feat(webowie): apply Odysseus intelligence suite" || true

cat <<MSG
Odysseus Intelligence Suite prepared at:
  $TARGET

Implemented in this channel revision:
  - standalone Intelligence Director
  - selectable Director endpoint and model per mission
  - Director API exempt from the global 45-second request timeout
  - plan approval before execution
  - adaptive research waves
  - evidence/audit trail
  - specialist worker routing
  - final synthesis
  - explicit Darknet/Tor approval gate

Approved specifications and implementation plans are installed into:
  docs/superpowers/specs/
  docs/superpowers/plans/

Next:
  cd "$TARGET"
  cp .env.example .env
  # configure your existing Lemonade/Search/Crawl4AI settings without committing secrets
  docker compose up -d --build
MSG
