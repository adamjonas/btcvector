from elasticsearch import Elasticsearch
import time
import json
from src.logger import LOGGER
from src.config import *


def extract_data_from_es(es_index):
    start_time = time.time()
    es = Elasticsearch(
        cloud_id=ES_CLOUD_ID,
        http_auth=(ES_USERNAME, ES_PASSWORD),
    )
    if es.ping():
        LOGGER.info("connected to the ElasticSearch")
        query = {
            "query": {
                "match_all": {}
            }
        }

        # Search the index
        results = es.search(index=es_index, body=query, size=ES_DATA_FETCH_SIZE)

        # Dump it into the json file
        LOGGER.info(f"Starting dumping of {es_index} data in json...")
        output_data_path = f'{DATA_PATH}/{es_index}.json'
        with open(output_data_path, 'w') as f:
            json.dump(results['hits']['hits'], f)
        LOGGER.info(
            f"Dumping of {es_index} data in json has completed ans has taken {time.time() - start_time:.2f} seconds.")

        return output_data_path
    else:
        LOGGER.info('Could not connect to Elasticsearch')
        return None