import logging
import os
import warnings
from datetime import datetime

from elasticsearch import Elasticsearch

from src.config import (
    DATA_PATH,
    ES_CLOUD_ID,
    ES_INDEX,
    ES_PASSWORD,
    ES_USERNAME,
    LOG_PATH,
)
from src.data_collection import extract_data_from_es
from src.data_insertion import pinecone_data_insertion
from src.logger import setup_logger
from src.utils import connect_to_pinecone_index, get_clean_json


warnings.filterwarnings("ignore")

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)

date = datetime.now().strftime("%Y_%m_%d")

log = setup_logger(
    out_file=f"{LOG_PATH}/es_to_pinecone_{date}.log", stderr_level=logging.INFO
)


def start_data_conversion():
    try:
        pinecone_index = connect_to_pinecone_index()
        es = Elasticsearch(
            cloud_id=ES_CLOUD_ID,
            http_auth=(ES_USERNAME, ES_PASSWORD),
        )
        output_data_path = extract_data_from_es(es, ES_INDEX)
        if output_data_path:
            json_data_path = get_clean_json(output_data_path)[0]
            pinecone_data_insertion(es, json_data_path, pinecone_index)
        else:
            log.info("No files left to upload.")
    except Exception as e:
        log.error(str(e))


if __name__ == "__main__":
    start_data_conversion()
