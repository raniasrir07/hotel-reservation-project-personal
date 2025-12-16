import os
import json
import logging
from datetime import datetime




def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO)

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')