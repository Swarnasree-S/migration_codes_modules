import uuid
import time
import config_loader

FOLDER_MAPPING = config_loader.config.get("folder_mapping", {})

def process_dashboard_json(dashboard_json, target_folder_name):
    dashboard_json["dashboard"]["tags"] = [FOLDER_MAPPING.get(target_folder_name, target_folder_name)]
    dashboard_json["dashboard"]["links"] = [{
        "title": target_folder_name,
        "url": f"/dashboards?folder={target_folder_name}",
        "type": "dashboards",
        "tags": [target_folder_name]
    }]
    dashboard_json["dashboard"]["id"] = None
    dashboard_json["dashboard"]["uid"] = f"{str(uuid.uuid4())[:8]}_{int(time.time())}"
    return dashboard_json
