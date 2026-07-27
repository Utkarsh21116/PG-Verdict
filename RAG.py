import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
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

embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vector_db = Chroma.from_texts(
    texts=[doc["page_content"] for doc in document],
    metadatas=[doc["metadata"] for doc in document],
    embedding=embedding,
    persist_directory="./pg_chroma_db"
)
