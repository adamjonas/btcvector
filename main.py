import logging
import os
import warnings
from datetime import datetime

from src.config import DATA_PATH, ES_INDEX, LOG_PATH
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
        total_inserted_data_count = pinecone_index.describe_index_stats()[
            "total_vector_count"
        ]
        if total_inserted_data_count == 0:
            log.info("Data collection from elastic-search started...")
            output_data_path = extract_data_from_es(ES_INDEX)
            # check we received a data path or not
            if output_data_path:
                json_data_path = get_clean_json(output_data_path)[0]
                pinecone_data_insertion(json_data_path, pinecone_index)
                log.info("PROCESS OF DATA INSERTION COMPLETED")
        else:
            # Next time we will just insert the data into pinecone,
            # not extract from ES.
            json_data_path = os.path.join(
                f"{DATA_PATH}", f"{ES_INDEX}_refined.json"
            )
            pinecone_data_insertion(
                json_data_path,
                pinecone_index,
                start_from=total_inserted_data_count,
            )
            log.info("PROCESS OF DATA INSERTION COMPLETED")

    except Exception as e:
        log.info(str(e))


if __name__ == "__main__":
    start_data_conversion()
