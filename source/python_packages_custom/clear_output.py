import os
import sys
import shutil
import json

SCRIPT_TITLE = "Albumus Clear Output"
LOG_TAG_CLEAR = "[🧹 Clear Output]"
LOG_TAG_CLEAR_SAFE = "[Clear Output]"

print(f'{LOG_TAG_CLEAR_SAFE} [Init] {SCRIPT_TITLE} Importing...')

# Path to this Python file
LOCATION_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.join(LOCATION_SCRIPT, '../../')

from cure_log import CureLog

logger = CureLog(os.path.join(DIR_ROOT, '_log/clear_output.log'))

logger.log("debug", LOG_TAG_CLEAR, "sys.path:", sys.path)
logger.log("init", LOG_TAG_CLEAR, "Import complete.")

# Load config/settings.json
settings_path = os.path.join(DIR_ROOT, 'config', 'settings.json')
config_dir = ""

try:
    with open(settings_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config_dir = os.path.abspath(config.get('dir'))
except Exception as e:
    logger.log("error", LOG_TAG_CLEAR, "Failed to load settings.json:", e)
    sys.exit(1)

# Define the full path to the 'out' directory
output_dir = os.path.join(config_dir, 'out')

logger.log("begin", LOG_TAG_CLEAR, "Running...")

if os.path.isdir(output_dir):
    try:
        shutil.rmtree(output_dir)
        logger.log("success", LOG_TAG_CLEAR, "Deleted directory:", {"path": output_dir})
    except Exception as e:
        logger.log("error", LOG_TAG_CLEAR, "Failed to delete output directory:", e)
        sys.exit(1)
else:
    logger.log("notice", LOG_TAG_CLEAR, "Output directory does not exist:", {"path": output_dir})

logger.log("end", LOG_TAG_CLEAR, "Complete.")
