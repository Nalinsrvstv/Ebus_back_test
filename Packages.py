# install_pipx_packages.py
import subprocess

with open('requirements.txt') as f:
    for line in f:
        package = line.strip()
        if package:  # Ensure the line isn't empty
            subprocess.run(['pipx', 'install', package])
