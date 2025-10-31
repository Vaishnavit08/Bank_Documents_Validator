import os
import io
import base64
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
from PIL import Image
import openai

# Load .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

PROMPT_TEMPLATE = """
You are a professional financial document analyzer.

Manual input:
- Account Holder Name: {user_name}
- Account Number: {user_number}
- IFSC Code: {user_ifsc}

Document Image: analyze the uploaded image/pdf

Tasks:
1. Extract EXACTLY:
   - Account Holder Name(you should accept case variations)
   - Account Number
   - IFSC Code


2. Compare with manual input:
   - For each field, mark as Match, Mismatch, or Not Found.

3. Return ONLY plain text in this format (professional table):

Field                 | Given             | Provided               | Status
Account Holder Name    | ...               | ...                    | Match/Mismatch
Account Number         | ...               | ...                    | Match/Mismatch
IFSC Code              | ...               | ...                    | Match/Mismatch

Final Summary: Concise summary explaining matches/mismatches.
"""

def call_gpt_vision(img_bytes, user_name, user_number, user_ifsc):
    base64_image = base64.b64encode(img_bytes).decode("utf-8")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT_TEMPLATE.format(
                    user_name=user_name,
                    user_number=user_number,
                    user_ifsc=user_ifsc
                )},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        }],
        max_tokens=1000
    )
    return response.choices[0].message.content

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    filename = file.filename.lower()
    file_bytes = file.read()

    # Convert PDF to image if needed
    if filename.endswith(".pdf"):
        pages = convert_from_bytes(file_bytes)
        img = pages[0]  # first page
    else:
        img = Image.open(io.BytesIO(file_bytes))

    # Convert to PNG bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    # Manual inputs
    user_name = request.form.get("acc_name", "")
    user_number = request.form.get("acc_number", "")
    user_ifsc = request.form.get("ifsc", "")

    try:
        result_text = call_gpt_vision(img_bytes, user_name, user_number, user_ifsc)
    except Exception as e:
        return f"OpenAI API error: {str(e)}", 500

    return result_text, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
 