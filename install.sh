#!/bin/bash
echo "[*] Installing SYRFO Tool..."
pip install requests --break-system-packages
sudo ln -sf "$(pwd)/SYRFO.py" /usr/bin/syrfo
sudo chmod +x /usr/bin/syrfo
echo "[+] Installation completed successfully!"
echo "[+] You can now use it anywhere like: syrfo -u syriatalk.org"