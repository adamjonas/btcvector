import os
from dotenv import load_dotenv
load_dotenv()

DATA_PATH = os.path.join(os.getcwd(), "data")
LOG_PATH = os.path.join(os.getcwd(), "logs")

MAX_TOKENS_PER_CHUNK = 8191  # chunk the text if it is greater than 8191 tokens

ES_CLOUD_ID= os.getenv("ES_CLOUD_ID")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
ES_INDEX = os.getenv("ES_INDEX")
ES_DATA_FETCH_SIZE = 10000  # No. of data to fetch and save from elastic-search


PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", default="text-embedding-ada-002")

NUM_RESULTS = 3  # how many top results wants in the output
