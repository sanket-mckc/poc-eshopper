from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Set your OpenAI API key here
client = OpenAI()
client.api_key = os.environ["OPENAI_API_KEY"]

def get_sales_assistant_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are furniture salesman working in the industry for more than 10+ years. Your job is to understand customer requests and suggest the best possible product/options to them out of the options available to you"},
            {"role": "user", "content": user_input},
        ]
    )
    return response

@app.route('/sales-assistant', methods=['POST'])
def sales_assistant():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    response = get_sales_assistant_response(user_input)
    return response.to_json()   

if __name__ == '__main__':
    app.run(debug=True)
