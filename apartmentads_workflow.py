import dlt
import requests
import json
import logging
from pathlib import Path
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#file path to the artifact directory in gihub actions
PROCESSED_IDS_FILE = './processed_ids/processed_ids.json'

def load_processed_ids(file_path):
    #checking if file path exists within the system, loading it if it does
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                logger.error(f"Error reading the file {file_path}. Starting with an empty set.")
                return set()
            
    #returning empty set if it doesn't exist
    else:
        return set()

def save_processed_ids(file_path, processed_ids):
    #checking if file path exists within the system
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:

            #loading the file into a set
            try:
                existing_ids = set(json.load(f)) 

            # or into an empty set if the file is corrupted
            except json.JSONDecodeError:
                existing_ids = set()

    #if file doesn't exist, create an empty set
    else:
        existing_ids = set()

    # Combine existing IDs with the new ones, excluding duplicates
    all_ids = existing_ids.union(processed_ids)

    with open(file_path, 'w') as f:
        # Convert set to list before saving
        json.dump(list(all_ids), f)

def _get_ads(url, max_retries, wait_time):
    #Fetching ads
    logger.info("Fetching ads from URL...")
    headers = {'accept': 'application/json'}
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers)
            #check status code
            response.raise_for_status() 
            logger.info(f"Successfully fetched data. Status Code: {response.status_code}")
            

            try:
                #making sure response is in json
                ads = response.json()
                logger.info(f"Fetched {len(ads)} ads.")
                return ads
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from the response.")
                return []   

        #handling if request fails, retrying after increasing breaks
        except requests.exceptions.RequestException as e:
            retries += 1
            wait_time += 90
            logger.error(f"Request failed (attempt {retries}/{max_retries}): {e}")
            if retries < max_retries:
                logger.info(f"Retrying in {wait_time} seconds... (Attempt {retries + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error("Max retries reached. Giving up.")
                return []

@dlt.resource
def apartmentsearch():
    logger.info("Apartmentsearch started...")
    url = 'https://bostad.stockholm.se/AllaAnnonser/'
    
    all_ads = []
    processed_ids = load_processed_ids(PROCESSED_IDS_FILE)
    new_ids = set()

    try:
        # Fetch all ads from the API
        response = _get_ads(url, max_retries = 5, wait_time = 60)
        if not response:
            logger.info("No ads found.")
            # If no ads are returned, return an empty list.
            return [] 

        logger.info(f"Fetched {len(response)} ads.")

        for ad in response:
            ad_id = ad.get("AnnonsId")
            if not ad_id:
                logger.warning("Ad without ID encountered. Skipping...")
                continue

            if ad_id not in processed_ids:
                logger.info(f"New ad found: ID {ad_id}")
                processed_ids.add(ad_id)
                new_ids.add(ad_id)
                all_ads.append(ad)
            else:
                pass

    except Exception as e:
        logger.error(f"Error while fetching ads: {e}")
    
    # Save processed IDs to jsonfile
    save_processed_ids(PROCESSED_IDS_FILE, processed_ids)

    # Return all the ads fetched
    if all_ads:
        yield all_ads
    else:
        logger.info("No new ads to process.")
        yield []


def run_pipeline(table_name):
    try:
        pipeline = dlt.pipeline(
            pipeline_name="apartmentads",
            destination="snowflake",
            dataset_name="Staging",
        )
        
        
        load_info = pipeline.run(apartmentsearch(), table_name=table_name)
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