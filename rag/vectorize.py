from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain.schema import Document
import params

# Step 1: Load CSV data using LangChain's CSVLoader
csv_loader = CSVLoader(file_path='../db/furniture_catalogue_updated_with_amazon_urls.csv')
data = csv_loader.load()

# Step 2: Process each Document object and create new Document objects with correct formatting
documents = []
for doc in data:
    # Extracting page_content from Document object
    page_content = doc.page_content.strip()
    
    # Assuming each field in page_content is separated by a newline and follows the "key: value" format
    fields = page_content.split('\n')
    row_dict = {}
    
    for field in fields:
        if ':' in field:
            key, value = field.split(':', 1)
            row_dict[key.strip()] = value.strip()

    # Create a document dictionary for each row
    doc_dict = {
        "furniture_name": row_dict.get('furniture_name', ''),
        "color_name": row_dict.get('color_name', ''),
        "color_hex_code": row_dict.get('color_hex_code', ''),
        "price": row_dict.get('price', ''),
        "dimensions": row_dict.get('dimensions', ''),
        "url": row_dict.get('url', ''),
        "text": (
            f"Furniture Name: {row_dict.get('furniture_name', '')} "
            f"Color Name: {row_dict.get('color_name', '')} "
            f"Color Hex Code: {row_dict.get('color_hex_code', '')} "
            f"Price: {row_dict.get('price', '')} "
            f"Dimensions: {row_dict.get('dimensions', '')}"
        )
    }
    
    # Create a Document object with updated text and metadata
    doc_object = Document(page_content=doc_dict["text"], metadata=doc_dict)
    documents.append(doc_object)

print(f'Loaded {len(documents)} documents')

# Step 3: Embed the text field
embeddings = OpenAIEmbeddings(api_key=params.openai_api_key, base_url=params.openai_api_base_url)

# Step 4: Store in MongoDB
client = MongoClient(params.mongodb_conn_string)
collection = client[params.db_name][params.collection_name]

# Reset collection without deleting the Search Index
collection.delete_many({})

# Initialize and store the documents in MongoDB Atlas with their embedding
docsearch = MongoDBAtlasVectorSearch.from_documents(
    documents, embeddings, collection=collection, index_name=params.index_name
)
