# Odysseus Intelligence Suite update channel

Use this file for the current installation/update procedure. The branch is intentionally separate from `main`.

## Fresh installation

```bash
git clone --branch odysseus-intelligence-suite --single-branch \
  https://github.com/puchadave/webOwie-Lokal.-Intelligent.-Dominanz..git \
  ~/odysseus-intelligence-channel

cd ~/odysseus-intelligence-channel
bash bootstrap.sh ~/odysseus-intelligence-suite
```

## Update an existing local Odysseus checkout

```bash
cd ~/odysseus-intelligence-channel
git pull
bash update.sh ~/odysseus

cd ~/odysseus
docker compose up -d --build
```

The updater creates a timestamped source backup before applying source changes and preserves `.env`, `data/`, `logs/`, and `.git`.

## Integrity model

The feature patch is stored as deterministic chunks under `payload/patch.part-*` because large GitHub Contents API writes are not reliable in this connector environment. `bootstrap.sh` and `update.sh`:

1. verify every chunk using `payload/CHUNK-SHA256SUMS`;
2. reconstruct and decompress the raw patch;
3. verify the raw patch SHA-256 `3cbfbad9760d64662c837fe6bad67b79f3261d9ed296c41eb218a73e5f48b129`;
4. run `git apply --check` before applying changes.

The patch is based on verified upstream Odysseus commit:

```text
25c9e735ef5ce605f47f8f666ac6689056d2c10c
```

## Current implementation state

Implemented now:
- standalone Intelligence Director in the left Odysseus menu;
- `/intelligence` program route;
- mission planning/PIRs/task graph;
- explicit plan approval before network execution;
- adaptive research waves and immutable plan versions;
- SearXNG/Crawl4AI/evidence integration;
- specialist model routing;
- final synthesis;
- explicit separate Darknet/Tor approval gate.

Approved specifications/plans:
- Model Hub as standalone Odysseus program;
- Hugging Face/GGUF/Safetensors import and conversion;
- all quantizations with sizes and multi-variant installation;
- AUTO/FIXED orchestrator role bindings;
- dynamic resource-aware routing per task;
- SPEED/QUALITY/BALANCED/LOW_MEMORY scheduler strategies;
- persistent import/conversion/benchmark queues and recovery;
- Deep Research methods `Classic`, `Intelligence Director`, and `Intelligence Director · Unfiltered`;
- standalone **Brand Studio / Full White-Label** program;
- custom logos, favicon, Light/Dark assets, login/report/e-mail branding and local fonts;
- structured design tokens instead of arbitrary CSS/JS;
- Draft → Validate → Preview → Publish with immutable published versions and rollback;
- granular branding permissions and authenticated preview sessions;
- global branding now with Domain/Organisation/Tenant-ready resolver architecture.

The Brand Studio specification and its three TDD plans are stored in the checksum-protected bundle under `design/brand-studio/`.

Model Hub, orchestrated Deep Research extensions, Unfiltered Research mode, and Brand Studio remain **design-and-plan state** until their implementation plans are executed. This channel does not pretend planned code already exists, because software has enough fictional status reporting without our assistance.
