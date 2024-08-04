from flask import Flask, request, jsonify, send_file
import requests
from io import BytesIO
import openai
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from PIL import Image

load_dotenv()

app = Flask(__name__)
openai_api_key = os.environ['OPENAI_API_KEY']
openai_base_url = os.environ['OPENAI_BASE_URL']
# Set your OpenAI API key here
client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    return image_data

def create_collage(images):
    # Define the size of the collage
    collage_width = 800
    collage_height = 600
    collage_image = Image.new('RGB', (collage_width, collage_height), color=(255, 255, 255))

    # Calculate the size of each image in the collage
    num_images = len(images)
    if num_images == 0:
        return None

    rows = cols = int(num_images ** 0.5)
    if rows * cols < num_images:
        cols += 1
    if rows * cols < num_images:
        rows += 1

    image_width = collage_width // cols
    image_height = collage_height // rows

    # Paste images into the collage
    for index, image in enumerate(images):
        img = Image.open(image)
        img.thumbnail((image_width, image_height))

        x = (index % cols) * image_width
        y = (index // cols) * image_height

        collage_image.paste(img, (x, y))

    collage_io = BytesIO()
    collage_image.save(collage_io, format='JPEG')
    collage_io.seek(0)

    return collage_io

@app.route('/download-images', methods=['POST'])
@cross_origin()
def download_images():
    image_urls = request.json.get('image_urls')
    if not image_urls or not isinstance(image_urls, list):
        return jsonify({"error": "Invalid or missing 'image_urls'"}), 400

    downloaded_images = []
    for url in image_urls:
        try:
            image_data = download_image(url)
            downloaded_images.append(image_data)
        except Exception as e:
            return jsonify({"error": f"Failed to download image from {url}: {str(e)}"}), 500

    # Create a collage from the downloaded images
    collage = create_collage(downloaded_images)
    if collage is None:
        return jsonify({"error": "Failed to create collage"}), 500

    return send_file(collage, mimetype='image/jpeg', as_attachment=True, download_name='collage.jpg')


def get_sales_assistant_response(user_input, old_message=None):
    start_prompt =  {"role": "system", "content": "As a seasoned furniture salesman with over 10 years of experience, greet the customer warmly and ask detailed questions about their space, provide furniture suggestions if required, style preferences, functional needs, budget to suggest the best possible options. I want you to ask me these questions one at a time making sure number of questions in total don't exceed more than 3 and should create a final confirmation message with all the requirements and make user confirm on it. Make sure the final confirmation message has room, style, furnitures and budget"}
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
@cross_origin()
def sales_assistant():
    if request.method == 'OPTIONS':
        # Handle CORS preflight requests
        return jsonify({"status": "ok"}), 200

    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    old_message = request.json.get('old_message')
    
    response = get_sales_assistant_response(user_input, old_message)
    return response.to_json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
