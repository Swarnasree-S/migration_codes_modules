import uuid
import time
import config_loader

FOLDER_MAPPING = config_loader.config.get("folder_mapping", {})

def process_dashboard_json(dashboard_json, target_folder_name):
    # Fetch mapped folder name or fallback to the target folder name
    mapped_folder = FOLDER_MAPPING.get(target_folder_name, target_folder_name)

    dashboard_json["dashboard"]["tags"] = [mapped_folder]
    dashboard_json["dashboard"]["links"] = [{
        "title": mapped_folder,
        "url": f"/dashboards?folder={mapped_folder}",
        "type": "dashboards",
        "tags": [mapped_folder],
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": False,
        "targetBlank": False
    }]
    
    # Clear the existing ID and generate a new unique ID
    dashboard_json["dashboard"]["id"] = None
    dashboard_json["dashboard"]["uid"] = f"{str(uuid.uuid4())[:8]}_{int(time.time())}"

   
    return dashboard_json
