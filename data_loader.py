# To add the data into the vector db
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from static_chatbot.constants import *
import time

embedding_model = CohereEmbeddings(model=EMBEDDING_MODEL)

def get_datastore():
    """Get the document retriever object to fetch the documents from vector database."""
    example_vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSISTENT_DIR,
    embedding_function=embedding_model
    )
    return example_vectorstore

datastore = get_datastore()
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
md_header_splits = splitter.split_text(text)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
splits = text_splitter.split_documents(md_header_splits)

for chunk_id in range(len(splits)):
    datastore.add_documents([splits[chunk_id]])
    if chunk_id % 99 == 0:
        print(chunk_id)
        print(splits[chunk_id])
        # Added sleep to not hit rate limit of cohere.
        time.sleep(60)
