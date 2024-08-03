import argparse
import params
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import warnings

# Filter out the UserWarning from langchain
warnings.filterwarnings("ignore", category=UserWarning, module="langchain.chains.llm")

# Process arguments
parser = argparse.ArgumentParser(description='Product Catalog Vector Search')
parser.add_argument('-q', '--question', help="The question to ask")
args = parser.parse_args()

if args.question is None:
    query = "Tell me the maximum price of the product?"

else:
    query = args.question

print("\nYour question:")
print("-------------")
print(query)

# Initialize MongoDB python client
client = MongoClient(params.mongodb_conn_string)
collection = client[params.db_name][params.collection_name]

# Initialize vector store
vectorStore = MongoDBAtlasVectorSearch(
    collection, OpenAIEmbeddings(api_key=params.openai_api_key, base_url=params.openai_api_base_url), index_name=params.index_name
)

# Perform a similarity search between the embedding of the query and the embeddings of the documents
print("---------------")
docs = vectorStore.max_marginal_relevance_search(query, K=5)

# Contextual Compression
llm = OpenAI(api_key=params.openai_api_key, base_url=params.openai_api_base_url, temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorStore.as_retriever()
)

print("\nAI Response:")
print("-----------")
compressed_docs = compression_retriever.get_relevant_documents(query)
# print(compressed_docs[0])
print(compressed_docs[0].page_content)
