# RasPy-Monitor
Monitoring tool for Raspberry Pi written in Python with Flask and Vue.js

## Configuration
Configuration is done with environment variables :
```sh
IGNORE_INTERFACES="lo eth0"
MOUNT_POINTS="/ /boot/efi"
DEBUG="1" 
```

## Usage
Launching from a virtual environment is recommended :
```sh
python3 -m venv virtualenv
source virtualenv/bin/activate  # Or use your shell equivalent
pip install -r requirements.txt
python3 app.py
```
