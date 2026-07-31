import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

with open('pg_essays/all_essays.json','r',encoding='utf-8') as f:
    essays = json.load(f)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False
)

document=[]

for essay in essays:
    chunks = text_splitter.split_text(essay['text'])

    for chunk in chunks:
        document.append({
            'page_content':chunk,
            'metadata':{
                'title':essay['title'],
                'url':essay['url'],
                "date": essay['date']
            }
        })

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma.from_texts(
    texts=[doc["page_content"] for doc in document],
    metadatas=[doc["metadata"] for doc in document],
    embedding=embeddings,
    persist_directory="./pg_chroma_db"
)

retriever = vector_db.as_retriever(search_type='similarity',search_kwargs={'k':4})

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory="./pg_chroma_db",
        embedding_function=embeddings
    )
    return vector_store.as_retriever(search_type='similarity',search_kwargs={'k':4})