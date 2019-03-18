#!/bin/bash -e

sudo apt install ipython3

chmod u+x bubbles.py bubbles.desktop
PATH=$(pwd)
sed -i "s/{SCRIPT_PATH}/${PATH}\/bubbles.py/" bubbles.desktop
mv bubbles.desktop ~/.local/share/applications/
mv snake_eye.png ~/.local/share/icons/

echo "Installed successfully"