import os
import json
import logging
import config_loader  # ✅ Import config module

# Configure Logging
logging.basicConfig(
    filename="migration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load DLID Mapping
dlid_map = config_loader.config.get("dlid_mapping", {})
if not dlid_map:
    print("\nWarning: No DLID mappings found in config.json")
    logging.warning("No DLID mappings found in config.json")

# Load DID Mapping (HT Meters, Inverters, etc.)
did_map = config_loader.config.get("did_mapping", {})
if not did_map:
    print("\nWarning: No DID mappings found in config.json")
    logging.warning("No DID mappings found in config.json")

def replace_dlid_and_did(json_data):
    try:
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    # Replace DLIDs
                    for old_dlid, new_dlid in dlid_map.items():
                        if old_dlid in value:
                            json_data[key] = value.replace(old_dlid, new_dlid)
                            logging.info(f"Replaced DLID {old_dlid} → {new_dlid} in key: {key}")
                    
                    # Replace DIDs (HT meters, Inverters, etc.)
                    for dlid, did_info in did_map.items():
                        for old_did, new_did in did_info.items():
                            if old_did in value:
                                json_data[key] = value.replace(old_did, new_did)
                                logging.info(f"Replaced DID {old_did} → {new_did} in key: {key}")
                else:
                    replace_dlid_and_did(value)
        elif isinstance(json_data, list):
            for item in json_data:
                replace_dlid_and_did(item)
    except Exception as e:
        logging.error(f"Error processing JSON data: {e}")
        print(f"\nError processing JSON data: {e}")
    return json_data

def update_dlid_and_did_in_dashboards():
    EXPORT_DIR = config_loader.config.get("export_dir", "exported_dashboards")
    print("\n🔄 Updating DLIDs and DIDs in exported dashboards...")

    for root, _, files in os.walk(EXPORT_DIR):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r") as file:
                        data = json.load(file)

                    updated_data = replace_dlid_and_did(data)

                    with open(file_path, "w") as outfile:
                        json.dump(updated_data, outfile, indent=4)
                        logging.info(f"Processed and updated: {file_path}")
                        print(f"Processed and updated: {file_path}")
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON file {file_path}: {e}")
                    print(f"Invalid JSON file {file_path}: {e}")
                except Exception as e:
                    logging.error(f"Error processing file {file_path}: {e}")
                    print(f"Error processing file {file_path}: {e}")

    print("\n✅ All dashboards updated successfully!")
