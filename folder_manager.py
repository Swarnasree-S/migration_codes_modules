import requests
import logging
import config_loader

TARGET_GRAFANA_URL = config_loader.get_grafana_urls()[1]
target_headers = config_loader.get_target_headers()

def create_target_folder(folder_name):
    folder_lookup = f"{TARGET_GRAFANA_URL}/api/folders"
    response = requests.get(folder_lookup, headers=target_headers)
    
    if response.status_code == 200:
        for folder in response.json():
            if folder["title"].lower() == folder_name.lower():
                return folder["id"]
    
    payload = {"title": folder_name}
    response = requests.post(f"{TARGET_GRAFANA_URL}/api/folders", headers=target_headers, json=payload)
    
    if response.status_code in [200, 201]:
        return response.json()["id"]
    else:
        logging.error(f"❌ Failed to create folder '{folder_name}': {response.json().get('message', 'Unknown error')}")
        return None
