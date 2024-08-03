from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import params

# Step 1: Load
# Load CSV data using LangChain's CSVLoader
csv_loader = CSVLoader(file_path='../db/furniture_catalog.csv')
data = csv_loader.load()

# Step 2: Transform (Split)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=0, 
    separators=["\n\n", "\n", "(?<=\. )", " "], 
    length_function=len
)
docs = text_splitter.split_documents(data)
print('Split into ' + str(len(docs)) + ' docs')

# Step 3: Embed
embeddings = OpenAIEmbeddings(api_key=params.openai_api_key, base_url=params.openai_api_base_url)

# Step 4: Store
# Initialize MongoDB python client
client = MongoClient(params.mongodb_conn_string)
collection = client[params.db_name][params.collection_name]

# Reset w/out deleting the Search Index
collection.delete_many({})

# Insert the documents in MongoDB Atlas with their embedding
docsearch = MongoDBAtlasVectorSearch.from_documents(
    docs, embeddings, collection=collection, index_name=params.index_name
)
