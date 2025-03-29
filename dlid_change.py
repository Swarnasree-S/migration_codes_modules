import os
import json
import logging
import config_loader  # ✅ Import config module

# Configure Logging
logging.basicConfig(filename="migration.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load DLID Mapping
dlid_map = config_loader.config.get("dlid_mapping", {})

if not dlid_map:
    print("\n Warning: No DLID mappings found in config.json")
    logging.warning("No DLID mappings found in config.json")

# Function to replace DLIDs recursively
def replace_dlid(json_data):
    try:
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    for old_dlid, new_dlid in dlid_map.items():
                        if old_dlid in value:
                            json_data[key] = value.replace(old_dlid, new_dlid)
                            logging.info(f"Replaced {old_dlid} → {new_dlid} in key: {key}")
                else:
                    replace_dlid(value)
        elif isinstance(json_data, list):
            for item in json_data:
                replace_dlid(item)
    except Exception as e:
        logging.error(f"Error processing JSON data: {e}")
        print(f"\n Error processing JSON data: {e}")
    return json_data

# Function to update DLIDs in exported dashboards
def update_dlid_in_dashboards():
    EXPORT_DIR = config_loader.config.get("export_dir", "exported_dashboards")  # ✅ Updated

    print("\n Updating DLIDs in exported dashboards...")

    for root, _, files in os.walk(EXPORT_DIR):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r") as file:
                        data = json.load(file)

                    updated_data = replace_dlid(data)

                    with open(file_path, "w") as outfile:
                        json.dump(updated_data, outfile, indent=4)
                        logging.info(f"\n Processed and updated: {file_path}")
                        print(f"\n Processed and updated: {file_path}")
                except json.JSONDecodeError as e:
                    logging.error(f"\n Invalid JSON file {file_path}: {e}")
                    print(f"\n Invalid JSON file {file_path}: {e}")
                except Exception as e:
                    logging.error(f"\n Error processing file {file_path}: {e}")
                    print(f"\n Error processing file {file_path}: {e}")

    print("\n All dashboards updated successfully!")

# Execute when run as a script
if __name__ == "__main__":
    update_dlid_in_dashboards()
