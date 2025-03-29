import os
import json
import requests
import logging
import config_loader
import json_processor

SOURCE_GRAFANA_URL = config_loader.get_grafana_urls()[0]
source_headers = config_loader.get_source_headers()
EXPORT_DIR = config_loader.config["export_dir"]

def get_source_folders():
    response = requests.get(f"{SOURCE_GRAFANA_URL}/api/folders", headers=source_headers)
    return response.json() if response.status_code == 200 else []

def fetch_dashboard_json(uid):
    response = requests.get(f"{SOURCE_GRAFANA_URL}/api/dashboards/uid/{uid}", headers=source_headers)
    return response.json() if response.status_code == 200 else None

def export_all():
    folders = get_source_folders()
    folder_dict = {folder["id"]: folder["title"] for folder in folders}
    folder_dict[0] = "General"

    for folder_id, folder_name in folder_dict.items():
        folder_export_path = os.path.join(EXPORT_DIR, folder_name)
        os.makedirs(folder_export_path, exist_ok=True)
        
        search_url = f"{SOURCE_GRAFANA_URL}/api/search?folderIds={folder_id}&type=dash-db"
        response = requests.get(search_url, headers=source_headers)

        if response.status_code != 200:
            logging.error(f"❌ Failed to get dashboards for '{folder_name}': {response.status_code}")
            continue

        for dashboard in response.json():
            uid = dashboard.get("uid")
            title = dashboard.get("title", "Untitled").replace(" ", "_")
            if uid:
                dashboard_json = fetch_dashboard_json(uid)
                if dashboard_json:
                    processed_json = json_processor.process_dashboard_json(dashboard_json, folder_name)
                    file_name = os.path.join(folder_export_path, f"{title}_{uid}.json")
                    with open(file_name, "w") as f:
                        json.dump(processed_json, f, indent=4)
                    logging.info(f"✅ Exported: {file_name}")
