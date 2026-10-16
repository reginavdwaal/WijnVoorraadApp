#!/bin/bash
# vino_config.sh - per-app deploy configuration, owned by this repo.
#
# Secret-free by design, so it is safe to commit. The release workflow
# (.github/workflows/release-deploy.yaml) rsyncs it to ~/domains/vino_config.sh on every
# deploy, where activate.sh / rollback.sh (from www_installer) source it. Real secrets live
# in shared/vino/.env on the server (see deploy/README.md).

DOMAIN="vino.vdwaal.net"
DOMAIN_BASE_DIR="/home/vdwanet/domains/"      # must have trailing slash
VERSION_FILE="WijnProject/__init__.py"        # file containing __version__ = "x.y.z"
PYTHON_ENV="/home/vdwanet/virtualenv/domains/vino.vdwaal.net/3.11/bin/activate"
# activate.sh defaults DJANGO_SETTINGS_MODULE to config.settings.prod; this project's
# settings package differs, so it MUST be set explicitly here.
DJANGO_SETTINGS_MODULE="WijnProject.settings.prod"

DATABASE_ENGINE="sqlite"                      # sqlite | mysql
# production = the live database persists in shared/vino/db.sqlite3, is backed up and
# migrated on every deploy. (The db.sqlite3 tracked in git is the dev database and is
# never shipped.)
DATABASE_SOURCE="production"

# "release_path:shared_name": uploaded label photos. prod.py serves MEDIA_ROOT from
# public_html/media, so that path becomes a symlink to shared/vino/media.
SHARED_PATHS=("public_html/media:media")

# How many pre-migrate SQLite backups to keep in shared/vino/ (needs the sqlite3 CLI).
# SQLITE_BACKUP_KEEP=10

# Used by the GitHub Actions smoke test after activation. The home page requires login,
# so use the login page, which answers 200 without a session.
SMOKE_URL="https://vino.vdwaal.net/accounts/login/"
