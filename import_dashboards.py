import os
import json
import requests
import logging
import config_loader
import json_processor
import folder_manager

TARGET_GRAFANA_URL = config_loader.get_grafana_urls()[1]
target_headers = config_loader.get_target_headers()
EXPORT_DIR = config_loader.config["export_dir"]

def import_dashboard(file_path, folder_id, target_folder_name):
    with open(file_path, "r") as f:
        dashboard_json = json.load(f)

    dashboard_json = json_processor.process_dashboard_json(dashboard_json, target_folder_name)
    payload = {"dashboard": dashboard_json["dashboard"], "overwrite": False, "folderId": folder_id, "message": "Imported via API"}

    response = requests.post(f"{TARGET_GRAFANA_URL}/api/dashboards/db", headers=target_headers, json=payload)
    if response.status_code in [200, 201]:
        logging.info(f"✅ Imported: {os.path.basename(file_path)} to {target_folder_name}")
    else:
        logging.error(f"❌ Failed to import {file_path} | Reason: {response.json().get('message', 'Unknown error')}")

def import_all():
    for folder_name in os.listdir(EXPORT_DIR):
        folder_path = os.path.join(EXPORT_DIR, folder_name)
        if os.path.isdir(folder_path):
            folder_id = folder_manager.create_target_folder(folder_name)
            if folder_id is None:
                continue
            for file_name in os.listdir(folder_path):
                import_dashboard(os.path.join(folder_path, file_name), folder_id, folder_name)
