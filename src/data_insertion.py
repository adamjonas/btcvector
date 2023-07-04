from src.logger import LOGGER
from src.config import *
from src.utils import connect_to_pinecone_index, split_text
from tqdm.auto import tqdm
import time
import json
import openai
openai.api_key = OPENAI_API_KEY


def individual_data_insertion(pinecone_index, embed, data):
    url = data['url']
    if data['url'] is None:
        url = "No url in data"
        
    text = data['clean_text']
    if isinstance(text, list):
        text = " ".join(text)
    # we shorten the text and give link if text size exceed
    if len(text.encode('utf-8')) > 30000:
        text = split_text(text, 30)[0] + f"...for more details you can click on below link\n {data['url']}"
    
    id = [data['es_id']]

    domain = data['domain']
    if data['domain'] is None:
        domain = ""

    created_at = data['created_at']
    if data['created_at'] is None:
        created_at = ""

    metadata_id = data['id']
    if data['id'] is None:
        metadata_id = ""
    
    title = data['title']
    if data['title'] is None:
        title = ""
    
    type_ = data['type']
    if data['type'] is None:
        type_ = ""
    
    authors = data['authors']
    if data['authors'] is None:
        authors = ""


    meta_data = [{
        'domain': domain,
        'created_at': created_at,
        'id': metadata_id,
        'title': title,
        'text': text,
        'type': type_,
        'url': url,
        'authors': authors
    }]

    to_upsert = list(zip(id, embed, meta_data))

    # connect and upsert to Pinecone
    pinecone_index.upsert(vectors=to_upsert)


def data_embed_insertion(pinecone_index, data, start_from):
    LOGGER.info("Generating of embeddings of text and insertion of data started...")
    start_time = time.time()
    embeds = []
    completed_row_count = 0
    for i in tqdm(range(start_from, len(data))):
        LOGGER.info(f"Processing row number: {i}")
        # create embeddings (try-except added to avoid RateLimitError)
        try:
            text = data[i]["clean_text"]
            if isinstance(text, str):
                res = openai.Embedding.create(input=[text], engine=OPENAI_EMBED_MODEL)
                embed = res['data'][0]['embedding']
                individual_data_insertion(pinecone_index, [embed], data[i])
            else:
                embed = []
                for text_chunk in text:
                    try:
                        res_chunk = openai.Embedding.create(input=[text_chunk], engine=OPENAI_EMBED_MODEL)
                        embed_chunk = res_chunk['data'][0]['embedding']
                        embed.append(embed_chunk)
                    except Exception as e:
                        LOGGER.info(str(e))
                        LOGGER.info(f"Error generated in completion: {i}")
                        time.sleep(120)
                        res_chunk = openai.Embedding.create(input=[text_chunk], engine=OPENAI_EMBED_MODEL)
                        embed_chunk = res_chunk['data'][0]['embedding']
                        embed.append(embed_chunk)

                individual_data_insertion(pinecone_index, embed, data[i])

            LOGGER.info(f"{i} rows inserted into pinecone.")
            embeds.append(embed)
            completed_row_count = i
        except Exception as e:
            LOGGER.info(str(e))
            LOGGER.info(f"Error generated in completion: {i}")
            time.sleep(120)
            text = data[i]["clean_text"]
            if isinstance(text, str) and not "This model's maximum context length is 8191 tokens" in str(e):
                res = openai.Embedding.create(input=[text], engine=OPENAI_EMBED_MODEL)
                embed = res['data'][0]['embedding']
                individual_data_insertion(pinecone_index, [embed], data[i])
            elif isinstance(text, str) and "This model's maximum context length is 8191 tokens" in str(e):
                embed = []
                text_chunk = split_text(text, max_tokens=MAX_TOKENS_PER_CHUNK // 2)
                for chunk_of_text_chunk in text_chunk:
                    try:
                        chunk_res_chunk = openai.Embedding.create(input=[chunk_of_text_chunk],
                                                                  engine=OPENAI_EMBED_MODEL)
                        chunk_embed_chunk = chunk_res_chunk['data'][0]['embedding']
                        embed.append(chunk_embed_chunk)
                    except Exception as e:
                        LOGGER.info(f"error generated in {i}")
                        LOGGER.info(f"error:- {str(e)}")
                        time.sleep(120)
                        chunk_res_chunk = openai.Embedding.create(input=[chunk_of_text_chunk],
                                                                  engine=OPENAI_EMBED_MODEL)
                        chunk_embed_chunk = chunk_res_chunk['data'][0]['embedding']
                        embed.append(chunk_embed_chunk)
                individual_data_insertion(pinecone_index, embed, data[i])

            else:
                embed = []
                for text_chunk in text:
                    try:
                        res_chunk = openai.Embedding.create(input=[text_chunk], engine=OPENAI_EMBED_MODEL)
                        embed_chunk = res_chunk['data'][0]['embedding']
                        embed.append(embed_chunk)
                    except Exception as e:
                        LOGGER.info(str(e))
                        LOGGER.info(f"Error generated in completion: {i}")
                        time.sleep(120)
                        if "This model's maximum context length is 8191 tokens" in str(e):
                            text_chunk = split_text(text_chunk, 500)
                            for chunk_of_text_chunk in text_chunk:
                                try:
                                    chunk_res_chunk = openai.Embedding.create(input=[chunk_of_text_chunk],
                                                                              engine=OPENAI_EMBED_MODEL)
                                    chunk_embed_chunk = chunk_res_chunk['data'][0]['embedding']
                                    embed.append(chunk_embed_chunk)
                                except:
                                    time.sleep(120)
                                    chunk_res_chunk = openai.Embedding.create(input=[chunk_of_text_chunk],
                                                                              engine=OPENAI_EMBED_MODEL)
                                    chunk_embed_chunk = chunk_res_chunk['data'][0]['embedding']
                                    embed.append(chunk_embed_chunk)
                        else:
                            res_chunk = openai.Embedding.create(input=[text_chunk], engine=OPENAI_EMBED_MODEL)
                            embed_chunk = res_chunk['data'][0]['embedding']
                            embed.append(embed_chunk)
                individual_data_insertion(pinecone_index, embed, data[i])

            embeds.append(embed)
            LOGGER.info(f"{i} rows inserted into pinecone.")
            completed_row_count = i

    LOGGER.info(f"Embeddings and insertion from {start_from} upto {completed_row_count} is completed and it took {time.time() - start_time:.2f} secs")
    return completed_row_count


def pinecone_data_insertion(json_data_path, pinecone_index, start_from=None):
    LOGGER.info("Generation and Insertion of embeddings of all data started...")
    start_time = time.time()
    file = open(json_data_path)
    data = json.load(file)

    if not start_from:
        start_from = 0

    if start_from != len(data):
        while start_from != len(data)-1:
            try:
                last_row = data_embed_insertion(pinecone_index, data, start_from)
                start_from = last_row
            except:
                pass
        LOGGER.info(f"Generation and Insertion of embeddings of all data completed and it took {time.time() - start_time:.2f} seconds.")
        file.close()
    else:
        LOGGER.info("Data has already been inserted")

