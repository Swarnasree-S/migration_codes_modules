import os
import json
import logging
import requests
import config_loader  # ✅ Import config_loader

# ========================== STEP 1: Load Configuration ==========================
# Use config_loader to get configuration values
config = config_loader.config

SOURCE_GRAFANA_URL, TARGET_GRAFANA_URL = config_loader.get_grafana_urls()
source_headers = config_loader.get_source_headers()
target_headers = config_loader.get_target_headers()
EXPORT_DIR = config["export_dir"]

# ========================== STEP 2: Configure Logging ==========================
logging.basicConfig(
    filename="migration.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# ========================== STEP 4: Fetch Data Sources from Grafana ==========================
def get_grafana_data_sources(url, headers):
    """Fetches all data sources from a given Grafana instance."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_sources = response.json()
        logging.info(f"Fetched {len(data_sources)} data sources from {url}")
        return {ds["uid"]: ds["name"] for ds in data_sources}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data sources from Grafana: {e}")
        return {}

# ========================== STEP 5: Update Data Source UID in JSON Dashboards ==========================
def update_datasource_uid(file_path, source_to_target_mapping): 
    """Recursively updates Data Source UIDs inside a JSON file."""
    try:
        with open(file_path, "r") as f:
            dashboard_json = json.load(f)
        
        updated = False  # Flag to check if updates were made

        def replace_uid(obj):
            nonlocal updated
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict) and "uid" in value and "datasource" in key:
                        old_uid = value["uid"]
                        if old_uid in source_to_target_mapping:
                            new_uid = source_to_target_mapping[old_uid]
                            logging.info(f"🔄 Updating Data Source UID: {old_uid} → {new_uid}")
                            value["uid"] = new_uid
                            updated = True
                    replace_uid(value)
            elif isinstance(obj, list):
                for item in obj:
                    replace_uid(item)

        replace_uid(dashboard_json.get("dashboard", {}))

        if updated:
            with open(file_path, "w") as f:
                json.dump(dashboard_json, f, indent=4)
            logging.info(f"✅ Data Source UID updated in: {file_path}")
        else:
            logging.info(f"No updates required for: {file_path}")

    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in file: {file_path}")
    except Exception as e:
        logging.error(f"An error occurred while processing {file_path}: {str(e)}")

# ========================== STEP 6: Main Function to Process Dashboards ==========================
def update_all_datasource_uids():
    """Main function to update all data source UIDs in exported dashboards."""
    logging.info("\n🔄 Updating Data Source UIDs...")

    source_data_sources = get_grafana_data_sources(SOURCE_GRAFANA_URL + "/api/datasources", source_headers)
    target_data_sources = get_grafana_data_sources(TARGET_GRAFANA_URL + "/api/datasources", target_headers)

    if not source_data_sources or not target_data_sources:
        logging.error("Could not fetch data sources from Grafana.")
        return

    source_to_target_mapping = {
        source_uid: target_uid
        for source_uid, source_name in source_data_sources.items()
        for target_uid, target_name in target_data_sources.items()
        if source_name == target_name
    }

    if not source_to_target_mapping:
        logging.error("No matching data sources found between source and target Grafana.")
        return

    for root, _, files in os.walk(EXPORT_DIR):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                update_datasource_uid(file_path, source_to_target_mapping)

    logging.info("\n✅ All Data Source UIDs Updated Successfully!")

if __name__ == "__main__":
    update_all_datasource_uids()
