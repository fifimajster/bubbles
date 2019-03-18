#!/bin/bash -e

# check os
uname_out=$(uname -s)
case ${uname_out} in
    Linux)      installer='sudo apt install' ;;
    Darwin)     installer='brew install' ;;
    *)          echo 'Your system is not supported, choose installer manually.'
                exit 1
esac

${installer} firefox
${installer} ipython3

cd ~/.mozilla/firefox/
cp -r *.default bubbles

while true; do
    read -p "Create dash shortcut? (tested on Ubuntu 18) [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Installed successfully"; exit;;
        * ) echo "Please answer y or n.";;
    esac
done

chmod u+x bubbles.py bubbles.desktop
PATH=$(pwd)
sed -i "s/{SCRIPT_PATH}/${PATH}\/bubbles.py/" bubbles.desktop
mv bubbles.desktop ~/.local/share/applications/
mv snake_eye.png ~/.local/share/icons/

echo "Installed successfully"