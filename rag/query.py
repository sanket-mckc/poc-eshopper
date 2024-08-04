import argparse
import params
from pymongo import MongoClient
from bson import ObjectId
from langchain_openai import OpenAI
import json
import re

# Process arguments
parser = argparse.ArgumentParser(description='Product Catalog Vector Search')
parser.add_argument('-q', '--question', help="The question to ask")
args = parser.parse_args()

# Default query if none is provided
if args.question is None:
    query = ("Thank you for sharing that! Here's a summary of your requirements for furnishing your study room: "
             "- **Room:** Study Room - **Color Preference:** ** Blue - **Furniture Needed:** ** Desk, Shelves, Chair - **Budget:** 10,000 INR "
             "Please confirm if everything looks good to you or if there's anything you'd like to change!")
else:
    query = args.question

print("\nYour question:")
print("-------------")
print(query)

# Initialize LLM
llm = OpenAI(api_key=params.openai_api_key, base_url=params.openai_api_base_url, temperature=0.7)

# Construct the prompt for extracting details
extraction_prompt = (
    "You are a helpful assistant tasked with extracting specific details from a query. "
    "Given the query below, extract the following details: Color Preferences, Furniture Needed, and Budget. "
    "Return the extracted details in a structured format.\n\n"
    "Query:\n"
    f"{query}\n\n"
    "Extracted Details:\n"
    "1. Color Preferences:\n"
    "2. Furniture Needed:\n"
    "3. Budget:\n"
)

# Generate the response from the LLM for extraction
extraction_response = llm(extraction_prompt)
print("\nExtracted Details:")
print(extraction_response)

# Parse the extracted details (assuming response is in JSON format)
try:
    extracted_details = json.loads(extraction_response)
except json.JSONDecodeError:
    print("Error decoding JSON from LLM response.")
    extracted_details = {}

# Extract details
colors = extracted_details.get("Color Preferences", [])
furniture_needed = extracted_details.get("Furniture Needed", [])
budget = extracted_details.get("Budget", None)

# Process colors (ensure it is a list of strings)
colors = [color.strip() for color in colors if color.strip()]

# Initialize MongoDB client
client = MongoClient(params.mongodb_conn_string)
collection = client[params.db_name][params.collection_name]

# Create a filter for the MongoDB query
filters = {}
if colors:
    filters['color_name'] = {'$in': colors}
if furniture_needed:
    filters['furniture_name'] = {'$in': furniture_needed}
if budget is not None:
    filters['price'] = {'$lte': budget}

# Retrieve all documents with specified filters
print("---------------")
docs = list(collection.find(filters).limit(45))

# Print the number of documents fetched
print(f"Number of documents fetched: {len(docs)}")

# Format documents for LLM input
formatted_docs = "\n".join(
    [f"ID: {str(doc.get('_id'))}\n"
     f"Color Name: {doc.get('color_name')}\n"
     f"Color Hex Code: {doc.get('color_hex_code')}\n"
     f"Price: {doc.get('price')}\n" for doc in docs]
)

# Construct the LLM prompt for combination search
search_prompt = (
    f"Here is a list of furniture items:\n\n{formatted_docs}\n\n"
    f"Based on the following query, find the best combinations of furniture:\n\n"
    f"Query: {query}\n\n"
    "Provide 3 combinations of furniture as specified in the query, each combination including the number of different types of furniture mentioned in the query. "
    "Each combination should not exceed the specified budget. Return only the IDs of the furniture items in each combination.\n\n"
    "Format the result as follows:\n"
    "{\n"
    "  'options': [\n"
    "    {\n"
    "      'items': [\n"
    "        {'id': 'document_id_1'},\n" 
    "        {'id': 'document_id_2'},\n"
    "        ... (up to number of items per combination mentioned in the query)\n"
    "      ]\n"
    "    },\n"
    "    ... (up to number of combinations mentioned in the query)\n"
    "  ]\n"
    "}\n"
    "Strictly adhere to the formatting in JSON structure.\n"
    "Ensure the IDs are unique and each combination is valid.\n"
)

# Generate the response from the LLM
response = llm(search_prompt)

# Print the response
print("\nGenerated combinations:")
print(response)

# Function to clean and convert the response to valid JSON
def clean_response(response_str):
    # Replace single quotes with double quotes
    json_str = response_str.replace("'", '"')
    # Ensure proper JSON formatting, e.g., fix trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    # Combine multiple JSON objects into a list
    json_str = re.sub(r'(?<=\})\s*(?=\{)', ', ', json_str)
    return json_str

try:
    # Clean and parse the response
    response_json = json.loads(clean_response(response))
except json.JSONDecodeError as e:
    print(f"JSON decoding error: {e}")
    response_json = {}

# Function to fetch details for the given IDs
def fetch_details_for_ids(ids):
    # Convert IDs to ObjectId format
    id_objects = [ObjectId(id_str.replace('ID: ', '')) for id_str in ids]
    # Fetch documents from MongoDB
    details = list(collection.find({'_id': {'$in': id_objects}}))
    return details

# Process the cleaned and parsed response
expanded_details = []
for option in response_json.get('options', []):
    expanded_option = {'items': []}
    for item in option.get('items', []):
        doc_id = item.get('id')
        details = fetch_details_for_ids([doc_id])
        if details:
            # Use the first matching document (assumes unique IDs)
            doc = details[0]
            expanded_option['items'].append({
                'id': str(doc.get('_id')),
                'furniture_name': doc.get('furniture_name'),
                'color_name': doc.get('color_name'),
                'color_hex_code': doc.get('color_hex_code'),
                'price': doc.get('price'),
                'dimensions': doc.get('dimensions'),
                'url': doc.get('url')
            })
    expanded_details.append(expanded_option)

# Print the expanded details
print("\nExpanded details:")
print(json.dumps({'options': expanded_details}, indent=2))
