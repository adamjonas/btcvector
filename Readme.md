# Data conversion from elastic search to pinecone from chaincode seminars data

Main goal is to make search queries/chatbot from pinecone instead of elastic-search

Required python>=3.9 and install all dependencies using:
- pip install requirements.txt

Set up environment variables: Create .env file in the root folder and add following keys -
```commandline
ES_CLOUD_ID = ""
ES_USERNAME = ""
ES_PASSWORD = ""
ES_INDEX = ""

PINECONE_INDEX_NAME = ""
PINECONE_API_KEY = ""
PINECONE_ENVIRONMENT = ""

OPENAI_API_KEY = ""
OPENAI_EMBED_MODEL = ""
```


For data conversion run:
- python main.py

To run flask-app(for api) run:
- python flask_app.py
- api url:- http://localhost:5000/search
- method: POST
- In api input should in json for example:- {"query":"what is bitcoin"}
- It will return the dictionary of top 3 results of title, url and text
