import logging
import time
import shutil
import os
import config_loader
import export_dashboards
import duid_change
import dlid_change
import import_dashboards



# Configure logging
with open("migration.log", "w"):
    pass

logging.basicConfig(
    filename="migration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set timezone
os.environ['TZ'] = 'Asia/Kolkata'
time.tzset()

# Load Configuration
config = config_loader.config
EXPORT_DIR = config["export_dir"]

# Setup export directory
if os.path.exists(EXPORT_DIR):
    shutil.rmtree(EXPORT_DIR)
os.makedirs(EXPORT_DIR, exist_ok=True)

if __name__ == "__main__":
    print("\n🔄 Exporting Dashboards...")
    export_dashboards.export_all()

    print("\n🔄 Updating Data Source UIDs...")
    duid_change.update_all_datasource_uids()

    print("\n🔄 Updating DLIDs...")
    dlid_change.update_dlid_in_dashboards()

    print("\n🔄 Importing Dashboards...")
    import_dashboards.import_all()

    print("\n🎉 Migration Completed!")
