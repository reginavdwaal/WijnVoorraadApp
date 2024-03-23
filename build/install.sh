#!/bin/bash

GITHUB_URL=https://github.com/reginavdwaal/WijnVoorraadApp.git
DOMAIN=vino.vdwaal.net
APP=vino

# Check if the release tag argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <release-tag>"
    echo ""
    echo "Current tags:"
    git ls-remote --tags $GITHUB_URL | gawk '{print substr($2,11)}'
    exit 1
fi

RELEASE_TAG="$1"
NEW_PATH="./$APP_$RELEASE_TAG"
SRC_PATH="./$APP_source_$RELEASE_TAG"

cd ~/domains/ || exit

# Ensure the checklist_new directory exists
mkdir -p "$NEW_PATH"

# Clone the repository into CLONE_PATH with the specified RELEASE_TAG
git clone --branch "$RELEASE_TAG" "$GITHUB_URL" "$SRC_PATH"

# Copy the required files and directories from the cloned directory
cp -r "$SRC_PATH/WijnVoorraad" "$NEW_PATH/"
cp -r "$SRC_PATH/WijnProject" "$NEW_PATH/"
cp "$SRC_PATH/passenger_wsgi.py" "$NEW_PATH/"
cp "$SRC_PATH/manage.py" "$NEW_PATH/"
cp "$SRC_PATH/requirements.txt" "$NEW_PATH/"

tar -cvzf $APP_current.tar.gz $DOMAIN/

