import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

with open('pg_essays\all_essays.json','r',encoding='utf-8') as f:
    essays = json.load(f)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False
)

document=[]
count=0
for essay in essays:
    count+=1
    print(essay['title'])
print(count)
