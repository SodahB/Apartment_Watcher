import dlt
import requests
import json
from pathlib import Path
import os

processed_ids = set()

def _get_ads(url):
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))

#@dlt.resource(write_disposition="replace")
def apartmentsearch():
    url = 'https://bostad.stockholm.se/AllaAnnonser/'
    print(url)
    while True:
        response = _get_ads(url, ad_id)
        print(response)

        if not response:
            print(f"No more results found.") 
            break 

        new_ads_found = False
        for ad in response:
            ad_id = ad.get("AnnonsId")
            print(ad_id)
            if ad_id and ad_id not in processed_ids:
                processed_ids.add(ad_id)
                yield ad
                new_ads_found = True
            elif ad_id:
                print(f"Duplicate ad ID found: {ad_id}") 

        if not new_ads_found:
            break 

if __name__ == "__main__":
    apartmentsearch()

# def run_pipeline(query, table_name):
#     pipeline = dlt.pipeline(
#         pipeline_name="jobsearch",
#         destination="snowflake",
#         dataset_name="staging"
#     )

#     params = {"q": query}
#     print(f"Running pipeline")
#     load_info = pipeline.run(jobsearch_resource(params=params), table_name=table_name)
#     print(load_info)

# if __name__ == "__main__":
#     working_directory = Path(__file__).parent
#     os.chdir(working_directory)

#     query = ["ekonomi", "economy", "ekonom", "account manager", "invest", "investment", "bank", "redovisning", "administratör"]

#     table_name = "econom_field_ads"

#     run_pipeline(query, table_name)