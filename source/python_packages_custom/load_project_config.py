import os
import json

def load_project_config(default_config_path, project_config_path):
    def read_config(path):
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}

    default_config = read_config(default_config_path)
    project_config = read_config(project_config_path)

    # Merge (project overrides default)
    merged_config = {**default_config, **project_config}
    return merged_config
