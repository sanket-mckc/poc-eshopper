import argparse
import params
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms import OpenAI
import warnings

# Suppress deprecated warnings and non-critical warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain.chains.llm")
warnings.simplefilter("ignore", category=DeprecationWarning)

# Process arguments
parser = argparse.ArgumentParser(description='Product Catalog Vector Search')
parser.add_argument('-q', '--question', help="The question to ask")
args = parser.parse_args()

if args.question is None:
    query = "give me blue colour furniture items"
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
docs = vectorStore.max_marginal_relevance_search(query, K=150)

# Initialize the LLM
llm = OpenAI(api_key=params.openai_api_key, base_url=params.openai_api_base_url, temperature=0.7)

# Format documents for LLM input
formatted_docs = "\n".join(
    [f"ID: {doc.get('_id')}\n"
     f"Furniture Name: {doc.get('furniture_name')}\n"
     f"Color Name: {doc.get('color_name')}\n"
     f"Color Hex Code: {doc.get('color_hex_code')}\n"
     f"Price: {doc.get('price')}\n"
     f"Dimensions: {doc.get('dimensions')}\n"
     f"URL: {doc.get('url')}\n" for doc in docs]
)

# Construct the LLM prompt
prompt = (
    f"Here is a list of furniture items:\n\n{formatted_docs}\n\n"
    f"Based on the following query, find the best combinations of furniture:\n\n"
    f"Query: Show me 4 combinations for furnishing a room, each combination with 4 different types of furniture: <desk, table, chair, lamp> where each set should not exceed a budget of 15000 INR. Include the best combinations of these furniture types within the budget\n\n"
    "Provide 4 combinations of furniture, each combination including 4 different types of furniture (desk, table, chair, lamp). "
    "Each combination should not exceed the specified budget. Return only the IDs of the furniture items in each combination.\n\n"
    "Format the result as follows:\n"
    "{\n"
    "  'options': [\n"
    "    {\n"
    "      'items': [\n"
    "        {'id': 'furniture_id_1'},\n"
    "        {'id': 'furniture_id_2'},\n"
    "        {'id': 'furniture_id_3'},\n"
    "        {'id': 'furniture_id_4'}\n"
    "      ]\n"
    "    },\n"
    "    ... (up to 4 combinations)\n"
    "  ]\n"
    "}\n"
)

# Generate the response from the LLM
response = llm(prompt)

# Print the response
print("\nGenerated combinations:")
print(response)
