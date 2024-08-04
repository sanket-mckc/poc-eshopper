import base64
from flask import Flask, request, jsonify, send_file, url_for
import requests
from io import BytesIO
import openai
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

app = Flask(__name__)
openai_api_key = os.environ['OPENAI_API_KEY']
openai_base_url = os.environ['OPENAI_BASE_URL']
client = openai.OpenAI(api_key=openai_api_key, base_url=openai_base_url)

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    return Image.open(image_data)

def create_collage(images, title, colors):
    collage_width = 1000
    collage_height = 1400
    collage_image = Image.new('RGB', (collage_width, collage_height), color=(255, 255, 255))

    draw = ImageDraw.Draw(collage_image)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    title_text = title
    text_bbox = draw.textbbox((0, 0), title_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.text(((collage_width - text_width) / 2, 20), title_text, fill="black", font=font)

    # Add color circles using the colors from the items
    circle_diameter = 60
    circle_positions = [(240, 80), (440, 80), (640, 80)]
    for color, pos in zip(colors, circle_positions):
        draw.ellipse([pos, (pos[0] + circle_diameter, pos[1] + circle_diameter)], fill=color)

    num_images = len(images)
    rows = (num_images + 1) // 2
    image_width = (collage_width - 120) // 2  # Adjusted to account for the right margin
    image_height = (collage_height - (rows + 1) * 40 - 200) // rows

    positions = []
    for row in range(rows):
        for col in range(2):
            if len(positions) < num_images:
                x = 40 + col * (image_width + 40)
                y = 200 + row * (image_height + 40)
                positions.append((x, y))

    for index, (img, pos) in enumerate(zip(images, positions)):
        img_resized = img.resize((image_width, image_height), Image.LANCZOS)
        collage_image.paste(img_resized, pos)

    collage_io = BytesIO()
    collage_image.save(collage_io, format='JPEG')
    collage_io.seek(0)

    # Convert to Base64
    collage_base64 = base64.b64encode(collage_io.getvalue()).decode('utf-8')

    return collage_base64

@app.route('/download-images', methods=['POST'])
@cross_origin()
def download_images():
    options = request.json.get('options')
    if not options or not isinstance(options, list):
        return jsonify({"error": "Invalid or missing 'options'"}), 400

    updated_options = []

    for option in options:
        items = option.get('items', [])
        image_urls = [item['url'] for item in items]
        colors = [item['color_hex_code'] for item in items[:3]]  # Get the first 3 colors
        if not image_urls:
            continue

        downloaded_images = []
        for url in image_urls:
            try:
                image = download_image(url)
                if image.format == "WEBP":
                    image = image.convert("RGBA")
                downloaded_images.append(image)
            except Exception as e:
                return jsonify({"error": f"Failed to download image from {url}: {str(e)}"}), 500

        title = "Collage for Option"
        collage_base64 = create_collage(downloaded_images, title, colors)
        if collage_base64 is None:
            return jsonify({"error": "Failed to create collage"}), 500

        option['collage_image_base64'] = collage_base64
        updated_options.append(option)

    return jsonify({"options": updated_options})

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
        return jsonify({"status": "ok"}), 200

    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    old_message = request.json.get('old_message')
    
    response = get_sales_assistant_response(user_input, old_message)
    return response.to_json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
