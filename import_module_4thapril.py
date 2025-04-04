import os
import json
import requests
import logging
import config_loader
import json_processor
import folder_manager

# 🔧 Config
TARGET_GRAFANA_URL = config_loader.get_grafana_urls()[1]
target_headers = config_loader.get_target_headers()
EXPORT_DIR = config_loader.config["export_dir"]

def import_dashboard(file_path, folder_id, target_folder_name):
    """
    Imports a single dashboard JSON file into the specified Grafana folder.
    """
    try:
        with open(file_path, "r") as f:
            dashboard_json = json.load(f)

        # 🧠 Pre-process dashboard JSON
        dashboard_json = json_processor.process_dashboard_json(dashboard_json, target_folder_name)

        payload = {
            "dashboard": dashboard_json["dashboard"],
            "overwrite": False,
            "folderId": folder_id,
            "message": "Imported via API"
        }

        response = requests.post(f"{TARGET_GRAFANA_URL}/api/dashboards/db", headers=target_headers, json=payload)
        if response.status_code in [200, 201]:
            logging.info(f"✅ Imported: {os.path.basename(file_path)} into '{target_folder_name}'")
        else:
            logging.error(f"❌ Failed to import '{file_path}' | Reason: {response.json().get('message', 'Unknown error')}")

    except Exception as e:
        logging.error(f"❌ Exception while importing '{file_path}': {str(e)}")

def import_all_dashboards():
    """
    Scans the export directory, creates folders in target Grafana, and imports dashboards.
    """
    if not os.path.exists(EXPORT_DIR):
        logging.error(f"🚫 Export directory not found: {EXPORT_DIR}")
        return

    for folder_name in os.listdir(EXPORT_DIR):
        folder_path = os.path.join(EXPORT_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        logging.info(f"\n📂 Processing folder: {folder_name}")
        folder_id = folder_manager.create_target_folder(folder_name)
        if folder_id is None:
            logging.error(f"🚫 Skipping folder due to creation error: {folder_name}")
            continue

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith(".json"):
                import_dashboard(file_path, folder_id, folder_name)

# ✅ You can call this from main_migration.py
# import_dashboards.import_all_dashboards()
