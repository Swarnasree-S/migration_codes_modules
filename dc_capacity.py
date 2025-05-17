import json
import logging
import os
import re
import config_loader  # Assuming your configuration loader is already imported

# Configure Logging
logging.basicConfig(
    filename="migration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load DC Capacity Mapping
dc_capacity_map = config_loader.config.get("dc_capacity_mapping", {})
if not dc_capacity_map:
    print("\nWarning: No DC Capacity mappings found in config.json")
    logging.warning("No DC Capacity mappings found in config.json")
def update_dc_capacity_for_new_dlid(json_data):
    """Update DC capacity for the new DLID in the JSON data."""
    try:
        if isinstance(json_data, dict):
            # Special handling for math expressions in InfluxDB queries
            if json_data.get("type") == "math" and isinstance(json_data.get("params"), list):
                for i, param in enumerate(json_data["params"]):
                    if isinstance(param, str):
                        for dlid, cap_info in dc_capacity_map.items():
                            old_capacity = str(cap_info.get("old")).strip()
                            new_capacity = str(cap_info.get("new")).strip()
                            if old_capacity in param:
                                json_data["params"][i] = param.replace(old_capacity, new_capacity)
                                logging.info(f"Replaced DC Capacity {old_capacity} → {new_capacity} in math param for DLID: {dlid}")
            else:
                for key, value in json_data.items():
                    if isinstance(value, str):
                        for dlid, cap_info in dc_capacity_map.items():
                            old_capacity = str(cap_info.get("old")).strip()
                            new_capacity = str(cap_info.get("new")).strip()
                            if old_capacity in value:
                                json_data[key] = value.replace(old_capacity, new_capacity)
                                logging.info(f"Replaced DC Capacity {old_capacity} → {new_capacity} for DLID: {dlid} in key: {key}")
                    else:
                        update_dc_capacity_for_new_dlid(value)
        elif isinstance(json_data, list):
            for item in json_data:
                update_dc_capacity_for_new_dlid(item)
    except Exception as e:
        logging.error(f"Error updating DC Capacity: {e}")
        print(f"\nError updating DC Capacity: {e}")
    return json_data


def update_dc_capacity_in_dashboards(EXPORT_DIR):
    """Loop through each exported dashboard JSON file and update DC Capacity values based on new DLID."""
    print("\n🔄 Updating DC Capacity values for new DLID in exported dashboards...")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for root, _, files in os.walk(EXPORT_DIR):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r") as file:
                        data = json.load(file)

                    # Update DC Capacity values in the JSON data
                    updated_data = update_dc_capacity_for_new_dlid(data)

                    # Save the updated dashboard
                    with open(file_path, "w") as outfile:
                        json.dump(updated_data, outfile, indent=4)
                        logging.info(f"✅ Processed and updated DC Capacity in: {file_path}")
                        print(f"✅ Processed and updated DC Capacity in: {file_path}")
                        updated_count += 1

                except json.JSONDecodeError as e:
                    logging.error(f"❌ Invalid JSON file {file_path}: {e}")
                    print(f"❌ Invalid JSON file {file_path}: {e}")
                    error_count += 1
                except Exception as e:
                    logging.error(f"❌ Error processing file {file_path}: {e}")
                    print(f"❌ Error processing file {file_path}: {e}")
                    error_count += 1

    print(f"\n🎉 DC Capacity update completed! ✅ {updated_count} updated, ⚠️ {skipped_count} skipped, ❌ {error_count} errors.")
    logging.info(f"DC Capacity update summary: Updated={updated_count}, Skipped={skipped_count}, Errors={error_count}")
