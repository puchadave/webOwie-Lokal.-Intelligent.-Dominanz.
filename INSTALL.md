# Installation and update

## Fresh

```bash
git clone --branch odysseus-intelligence-suite --single-branch \
  https://github.com/puchadave/webOwie-Lokal.-Intelligent.-Dominanz..git \
  odysseus-intelligence-channel
cd odysseus-intelligence-channel
bash bootstrap-fresh.sh ~/odysseus-intelligence-suite
```

## Existing local installation

```bash
cd ~/odysseus-intelligence-channel
git pull
bash update-existing.sh ~/odysseus
```

Then rebuild:

```bash
cd ~/odysseus
docker compose up -d --build
```

If the patch cannot be applied cleanly, the updater exits before applying it and points to the backup it created. It does not resolve conflicts by silently overwriting application source.
