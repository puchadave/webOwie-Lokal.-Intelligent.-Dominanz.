# Odysseus Intelligence Suite · webOwie update channel

This branch is a dedicated GitHub update channel for the webOwie/Odysseus Intelligence Suite.

## What this revision contains

**Implemented:** the standalone Odysseus **Intelligence Director** program, including plan review, explicit execution approval, adaptive research waves, evidence/audit storage, specialist worker routing, final synthesis, and the separate Darknet/Tor approval gate.

**Specified/planned, not falsely advertised as already implemented:** the standalone **Model Hub**, dynamic resource-aware model routing, Hugging Face/GGUF/Safetensors import and conversion, benchmarks, orchestrator profiles, and the two Director methods inside Deep Research including Unfiltered Research mode.

See `VERSION` and `channel.json` for the exact state.

## Fresh clone / installation

```bash
git clone --branch odysseus-intelligence-suite --single-branch \
  https://github.com/puchadave/webOwie-Lokal.-Intelligent.-Dominanz..git \
  odysseus-intelligence-channel

cd odysseus-intelligence-channel
bash bootstrap-fresh.sh ~/odysseus-intelligence-suite
```

The bootstrap script clones the official Odysseus repository and pins it to the verified base commit `25c9e735ef5ce605f47f8f666ac6689056d2c10c`, applies the webOwie Intelligence Suite patch, and installs the CPU/Lemonade compose overlays.

## Update an existing `~/odysseus`

```bash
git clone --branch odysseus-intelligence-suite --single-branch \
  https://github.com/puchadave/webOwie-Lokal.-Intelligent.-Dominanz..git \
  ~/odysseus-intelligence-channel

cd ~/odysseus-intelligence-channel
bash update-existing.sh ~/odysseus
```

For later channel updates:

```bash
cd ~/odysseus-intelligence-channel
git pull
bash update-existing.sh ~/odysseus
```

The updater verifies the patch checksum, creates a timestamped source backup first, and does not copy `.env`, `data/`, `logs/`, or Git metadata from the channel.

## Files

- `odysseus-intelligence-suite.patch.gz.b64` — compressed reproducible feature patch against the verified Odysseus base
- `overlays/docker-compose.yml` — webOwie CPU/Lemonade/Crawl4AI-aware compose configuration
- `overlays/docker-compose.5600G-CPU-optimized.yml` — Ryzen 5 5600G CPU-oriented compose profile
- `bootstrap-fresh.sh` — reproducible fresh checkout builder
- `update-existing.sh` — updater for an existing local Odysseus source tree
- `SHA256SUMS` — integrity hashes
- `VERSION` / `channel.json` — machine-readable update-channel state
- `DESIGN-AND-PLANS.md.gz.b64` — compressed bundle containing all approved design specifications and implementation plans

To extract the complete design/plan bundle:

```bash
base64 -d DESIGN-AND-PLANS.md.gz.b64 | gzip -dc > DESIGN-AND-PLANS.md
```

## Development model

This update channel is intentionally separate from the repository's normal `main` branch. Future implementation work for Model Hub and orchestrated Deep Research can be published to this same branch, so local installations have one stable update source instead of a growing pile of mystery patches.
