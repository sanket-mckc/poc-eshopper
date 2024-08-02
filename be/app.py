from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai_api_key = os.environ['OPENAI_API_KEY']
openai_base_url = os.environ['OPENAI_BASE_URL']
# Set your OpenAI API key here
client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)

def get_sales_assistant_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "As a seasoned furniture salesman with over 10 years of experience, greet the customer warmly and ask detailed questions about their space, style preferences, existing furniture, functional needs, budget, and timeframe to suggest the best possible options."},
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
