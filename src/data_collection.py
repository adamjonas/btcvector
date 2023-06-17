import json
import time

from elasticsearch import Elasticsearch

from src.config import (
    DATA_PATH,
    ES_CLOUD_ID,
    ES_DATA_FETCH_SIZE,
    ES_PASSWORD,
    ES_USERNAME,
)
from src.logger import LOGGER


def extract_data_from_es(es_index):
    start_time = time.time()
    es = Elasticsearch(
        cloud_id=ES_CLOUD_ID,
        http_auth=(ES_USERNAME, ES_PASSWORD),
    )
    if es.ping():
        LOGGER.info("connected to the ElasticSearch")
        query = {"query": {"match_all": {}}}

        # Search the index
        results = es.search(index=es_index, body=query, size=ES_DATA_FETCH_SIZE)

        # Dump it into the json file
        LOGGER.info(f"Starting dumping of {es_index} data in json...")
        output_data_path = f"{DATA_PATH}/{es_index}.json"
        with open(output_data_path, "w") as f:
            json.dump(results["hits"]["hits"], f)
        LOGGER.info(
            f"Dumping of {es_index} data in json has completed ans has taken "
            f"{time.time() - start_time:.2f} seconds."
        )

        return output_data_path
    else:
        LOGGER.info("Could not connect to Elasticsearch")
        return None
