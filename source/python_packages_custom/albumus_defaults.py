import os
import shutil
import sys

from cure_log import CureLog

LOG_TAG_DEFAULTS = '[📝 Defaults]'

# Compute absolute paths similar to getRootPath
def get_root_path(*relative_parts):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    return os.path.join(base_dir, *relative_parts)

log_file_path = os.path.join(get_root_path('_log'), 'defaults.log')
logger = CureLog(log_file_path)

# default file list
files_defaults = [
    "settings.json"
]

def configEnsure():
    logger.log("begin", LOG_TAG_DEFAULTS, "Initializing...")

    path_config_default = get_root_path('config', 'default')
    path_config = get_root_path('config')

    logger.log("info", LOG_TAG_DEFAULTS, 'Default Config Path:', path_config_default)
    logger.log("info", LOG_TAG_DEFAULTS, 'Config Path:', path_config)

    try:
        for file_name in files_defaults:
            default_file_path = os.path.join(path_config_default, file_name)
            target_file_path = os.path.join(path_config, file_name)

            if not os.path.exists(target_file_path):
                if os.path.exists(default_file_path):
                    shutil.copyfile(default_file_path, target_file_path)
                    logger.log("success", LOG_TAG_DEFAULTS, 'Initialized file from default:', default_file_path)
                else:
                    logger.log("error", LOG_TAG_DEFAULTS, 'Initialization failed, default file missing:', default_file_path)
                    sys.exit(1)
            else:
                logger.log("success", LOG_TAG_DEFAULTS, 'File already exists:', target_file_path)

    except Exception as e:
        logger.log("error", LOG_TAG_DEFAULTS, 'An error occurred during initialization:', str(e))
        sys.exit(1)

    logger.log("end", LOG_TAG_DEFAULTS, "Complete.")

if __name__ == "__main__":
    ansi = configEnsure()
