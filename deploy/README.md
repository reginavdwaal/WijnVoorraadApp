# Release & deploy

`poetry run cz bump` bumps the version, updates `CHANGELOG.md`, tags `vX.Y.Z` and pushes the
commit and tag (post-bump hook in `pyproject.toml`). The tag push triggers
`.github/workflows/release-deploy.yaml`:

1. **test**: the tag must match `__version__` in `WijnProject/__init__.py`, no missing
   migrations, `pytest`.
2. **release**: creates the GitHub release with generated notes.
3. **ship**: exports `requirements.txt` from `poetry.lock`, rsyncs the runtime tree to
   `~/domains/releases/vino_<tag>/` and `deploy/vino_config.sh` to `~/domains/vino_config.sh`.
4. **activate**: runs `~/deploy-tools/scripts/activate.sh vino <tag>` (from the
   `www_installer` repo): backs up the SQLite database, stops the app, swaps the directories,
   `pip install`, `migrate`, `collectstatic`, starts the app. Then a smoke test requests
   `SMOKE_URL`; on any failure the code is rolled back automatically.

Manual rollback (add `--restore-db` to also restore the database backup):

```bash
cd ~/domains && ~/deploy-tools/scripts/rollback.sh vino
```

## One-time setup

### 1. GitHub secrets

On `reginavdwaal/WijnVoorraadApp` (the same values as the other apps on this server):

```bash
gh secret set SSH_HOST        --repo reginavdwaal/WijnVoorraadApp
gh secret set SSH_USER        --repo reginavdwaal/WijnVoorraadApp
gh secret set SSH_PORT        --repo reginavdwaal/WijnVoorraadApp
gh secret set SSH_PRIVATE_KEY --repo reginavdwaal/WijnVoorraadApp < path/to/id_deploy
gh secret set SSH_KNOWN_HOSTS --repo reginavdwaal/WijnVoorraadApp < path/to/known_hosts
gh secret list --repo reginavdwaal/WijnVoorraadApp
```

### 2. Server (over SSH)

Details and reasoning: `BOOTSTRAP.md` in the `www_installer` repo. For this app:

```bash
cd ~/domains
mkdir -p releases shared/vino
LIVE=~/domains/vino.vdwaal.net; SHARED=~/domains/shared/vino

test -L "$LIVE" && echo "SYMLINK - fix per BOOTSTRAP.md" || echo "OK real directory"
command -v sqlite3        # needed for the pre-migrate backups

# Database
mv "$LIVE/db.sqlite3" "$SHARED/db.sqlite3" && ln -s "$SHARED/db.sqlite3" "$LIVE/db.sqlite3"

# Uploaded label photos (public_html/media)
mkdir -p "$SHARED/media"
mv "$LIVE/public_html/media/"* "$SHARED/media/" 2>/dev/null || true
rm -rf "$LIVE/public_html/media"
ln -s "$SHARED/media" "$LIVE/public_html/media"

# Secrets: take the values from the current environment, e.g.
#   grep -i SetEnv "$LIVE/public_html/.htaccess"
cat > "$SHARED/.env" << 'EOF'
SECRET_KEY=...
DB_PASSWORD=...
OPENAI_API_KEY=...
# OPENAI_MODEL=gpt-6.1-sol
EOF
chmod 600 "$SHARED/.env"
ln -sf "$SHARED/.env" "$LIVE/.env"
```

`~/deploy-tools` is cloned by the workflow if it is missing.

### 3. First deploy

The workflow has to exist in the tagged commit, so the first automated deploy is the first
bump after this was merged:

```bash
poetry run cz bump
gh run watch --repo reginavdwaal/WijnVoorraadApp
```

`activate.sh` refuses a tag that is already the running version, so deploy a new version.

## Legacy

`build/install.sh`, `build/deploy.sh`, `build/vino_config.sh` and `build/parse_env.sh` are the
old manual, interactive deploy. They are kept until the first automated deploy has succeeded,
then they can be deleted.
