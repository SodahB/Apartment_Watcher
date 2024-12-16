import dlt
import requests
import json
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_processed_ids(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                logger.error(f"Error reading the file {file_path}. Starting with an empty set.")
                return set()
    else:
        return set()

def save_processed_ids(file_path, processed_ids):
    with open(file_path, 'w') as f:
        json.dump(list(processed_ids), f)

processed_ids = set()

def _get_ads(url):
    logger.debug("Fetching ads from URL...")
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        #check status code
        response.raise_for_status() 
        logger.debug(f"Successfully fetched data. Status Code: {response.status_code}")
        

        try:
            #making sure response is in json
            ads = response.json()
            logger.debug(f"Fetched {len(ads)} ads.")
            return ads
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from the response.")
            return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []

@dlt.resource
def apartmentsearch():
    logger.debug("Apartmentsearch started...")
    url = 'https://bostad.stockholm.se/AllaAnnonser/'
    logger.debug(url)

    all_ads = []

    while True:
        try:
            response = _get_ads(url)
            if not response:
                logger.info("No more results found.")
                break
            logger.debug(f"Fetched {len(response)} ads.")
        except Exception as e:
            logger.error(f"Error while fetching ads: {e}")
            break

        new_ads_found = False

        for ad in response:
            ad_id = ad.get("AnnonsId")
            if not ad_id:
                logger.warning("Ad without ID encountered. Skipping...")
                continue
            
            if ad_id not in processed_ids:
                logger.debug(f"New ad found: ID {ad_id}")
                processed_ids.add(ad_id)
                all_ads.append(ad)
                new_ads_found = True
                print(ad)
            else:
                logger.debug(f"Duplicate ad skipped: ID {ad_id}")

        if not new_ads_found:
            logger.info("No new ads found in the current batch. Ending search.")
            break

    yield all_ads

def run_pipeline(table_name):
    try:
        pipeline = dlt.pipeline(
            pipeline_name="apartmentads",
            destination="snowflake",
            dataset_name="Staging",
        )
        
        
        load_info = pipeline.run(apartmentsearch(), table_name=table_name, overwrite=False)
        print("Pipeline ran successfully:", load_info)
    except Exception as e:
        print(f"An error occurred while running the pipeline: {e}")

if __name__ == "__main__":
    working_directory = Path(__file__).parent
    os.chdir(working_directory)
    logger.info("Starting script...")
    table_name = 'apartment_ads'
    try:
        run_pipeline(table_name)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
