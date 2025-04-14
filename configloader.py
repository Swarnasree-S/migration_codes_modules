import json

CONFIG_FILE = "config.json"

# ✅ Load config once at the start
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)  # ✅ Now `config_loader.config` is available globally

def get_source_headers():
    """Returns authentication headers for Source Grafana."""
    return {
        "Authorization": f"Bearer {config['source_api_key']}",
        "Content-Type": "application/json"
    }

def get_target_headers():
    """Returns authentication headers for Target Grafana."""
    return {
        "Authorization": f"Bearer {config['target_api_key']}",
        "Content-Type": "application/json"
    }

def get_grafana_urls():
    """Returns Source and Target Grafana URLs."""
    return config["source_grafana_url"], config["target_grafana_url"]

def get_new_folder_name():
    """Returns the target folder name from config."""
    return config.get("new_folder_name")    
