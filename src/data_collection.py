import json
import time

from src.config import DATA_PATH, ES_DATA_FETCH_SIZE
from src.logger import LOGGER


def extract_data_from_es(es, es_index):
    start_time = time.time()
    if es.ping():
        LOGGER.info("connected to the ElasticSearch")
        query = {
            "size": ES_DATA_FETCH_SIZE,
            "query": {
                "bool": {"must_not": {"term": {"upload_to_pinecone": 0}}}
            },
        }
        response = es.search(index=es_index, body=query, scroll="1m")
        scroll_id = response["_scroll_id"]
        total_results = response["hits"]["total"]["value"]
        if total_results == 0:
            LOGGER.info("No documents found.")
            return None

        search_results = response["hits"]["hits"]
        # Continue scrolling until all documents are retrieved
        while len(response["hits"]["hits"]) > 0:
            response = es.scroll(scroll_id=scroll_id, scroll="1m")
            scroll_id = response["_scroll_id"]
            # Check if no documents are returned
            if len(response["hits"]["hits"]) == 0:
                print("No more documents found.")
                break
            search_results += response["hits"]["hits"]

        LOGGER.info("Collected all the results from ElasticSearch")

        # Dump it into the json file
        LOGGER.info(f"Starting dumping of {es_index} data in json...")
        output_data_path = f"{DATA_PATH}/{es_index}.json"
        with open(output_data_path, "w") as f:
            json.dump(search_results, f)
        LOGGER.info(
            f"Dumping of {es_index} data in json has completed ans has taken "
            f"{time.time() - start_time:.2f} seconds."
        )

        return output_data_path
    else:
        LOGGER.error("Could not connect to Elasticsearch")
        return None
