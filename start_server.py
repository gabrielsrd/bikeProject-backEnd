#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir('/home/galves/gabriel/usp/tccBike/bikeProject-backEnd')
python_path = '/home/galves/gabriel/usp/tccBike/bikeProject-backEnd/.venv/bin/python'
result = subprocess.run([python_path, 'manage.py', 'runserver', '8000'])