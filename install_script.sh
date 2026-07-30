#!/bin/bash
mkdir -p bin
wget -P ./bin/astap_cli_zipped/ https://sourceforge.net/projects/astap-program/files/linux_installer/astap_command-line_version_Linux_aarch64.zip/download
unzip ./bin/astap_cli_zipped/download -d astap_cli_download
cp ./bin/astap_cli_download/astap_cli ./bin/astap_cli
rm -rf ./bin/astap_cli_download ./bin/astap_cli_zipped
# sudo apt install astap_cli

# TODO:
# Maybe change this index db to a different/better one
# - This is the ~5MB db for testing, maybe use d20 for real?
# - ask tom :))
wget https://sourceforge.net/projects/astap-program/files/star_databases/g05_star_database.deb/downloadmv download index-db-installer.deb

mv download ./index-db-installer.deb
sudo apt install ./index-db-installer.deb
sudo ln -s /opt/astap /usr/share/astap/data

sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
