import pandas as pd
from src.config import *
import pinecone
from src.logger import LOGGER
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

openai.api_key = OPENAI_API_KEY


def get_text_from_strdict(text):
    extracted_text_list = []
    if len(text) != 0 and type(text) == list:
        for values in text:
            dict_ = eval(values)
            if "text" in (dict_.keys()):
                extracted_text_list.append(dict_["text"])
            else:
                get_text_from_strdict(values)

    return extracted_text_list


def get_clean_text(text):
    if type(text) == str:
        return text
    elif type(text) == list:
        extracted_text_list = get_text_from_strdict(text)
        if len(extracted_text_list) != 0:
            extracted_text = " ".join(extracted_text_list)
            return extracted_text
        else:
            return text
    else:
        return ""


def split_text(text, max_tokens=MAX_TOKENS_PER_CHUNK):
    if text != "":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens,
            chunk_overlap=max_tokens // 10,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        LOGGER.info(f'Text split into {len(chunks)} parts')
        return chunks if len(chunks) > 1 else chunks[0]
    else:
        return ""


def get_clean_json(json_file):
    LOGGER.info("Preprocessing the json file")
    filename = json_file[:-5]
    df = pd.read_json(json_file)
    meta_data = [data for data in df["_source"]]
    meta_data_df = pd.DataFrame.from_dict(meta_data)
    # Remove bitcoin-talk forums from the data
    meta_data_df = meta_data_df[~meta_data_df.id.str.contains("bitcointalk")]
    try:
        meta_data_df.drop(
            ["thread_url", "transcript_by", "categories", "media", "tags", "language", "accepted_answer_id"],
            axis=1, inplace=True)
    except:
        pass
    meta_data_df["es_id"] = df["_id"]
    meta_data_df["clean_text"] = meta_data_df["body"].apply(get_clean_text)
    meta_data_df["clean_text"] = meta_data_df["clean_text"].apply(split_text)
    meta_data_df = meta_data_df[meta_data_df['clean_text'] != ""]
    csv_output_path = f"{filename}_refined.csv"
    json_output_path = f"{filename}_refined.json"
    meta_data_df.to_csv(csv_output_path)
    meta_data_df.to_json(json_output_path, orient="records")
    LOGGER.info("Preprocessed the json file")
    return json_output_path, csv_output_path


def connect_to_pinecone_index():
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )
    index = pinecone.Index(PINECONE_INDEX_NAME)
    # # view index stats
    # print(index.describe_index_stats())
    LOGGER.info("Connected to pinecone")

    return index


def decode_entries(entries):
    output_data = dict()
    for i, dict_ in enumerate(entries):
        output_data[str(i)] = {
            "url": dict_["metadata"]["url"],
            "title": dict_["metadata"]["title"],
            "document": dict_["metadata"]["text"],
            "authors": dict_["metadata"]["authors"],
        }
    return output_data


def query_index(query, index):
    res = openai.Embedding.create(
        input=[query],
        engine=OPENAI_EMBED_MODEL
    )
    vector = res['data'][0]['embedding']
    result = index.query(vector, top_k=NUM_RESULTS, include_metadata=True)
    return decode_entries(result.matches)


def query_index_by_author(query, index, author):
    res = openai.Embedding.create(
        input=[query],
        engine=OPENAI_EMBED_MODEL
    )
    vector = res['data'][0]['embedding']
    result = index.query(vector,
                         top_k=NUM_RESULTS,
                         include_metadata=True,
                         filter={
                             "authors": author
                         }
                         )
    return decode_entries(result.matches)
