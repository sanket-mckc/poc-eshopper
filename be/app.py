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

def get_sales_assistant_response(user_input, old_message=None):
    start_prompt =  {"role": "system", "content": "As a seasoned furniture salesman with over 10 years of experience, greet the customer warmly and ask detailed questions about their space, provide furniture suggestions if required, style preferences, functional needs, budget to suggest the best possible options. I want you to ask me these questions one at a time making sure number of questions in total don't exceed more than 3 and should create a final confirmation message with all the requirements and make user confirm on it."}
    if old_message:
        messages = [start_prompt]+ old_message + [user_input]
    else:
        messages = [
            start_prompt,
            user_input,
        ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response

@app.route('/sales-assistant', methods=['POST'])
def sales_assistant():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    old_message = request.json.get('old_message')
    
    response = get_sales_assistant_response(user_input, old_message)
    return response.to_json()   

if __name__ == '__main__':
    app.run(debug=True)
