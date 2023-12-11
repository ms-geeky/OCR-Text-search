from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the UPLOAD_FOLDER exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(request.url)

    file = request.files['image']

    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        unique_filepath = make_unique_filepath(filepath)
        file.save(unique_filepath)
        text = extract_text(unique_filepath)  # Pass the filepath as an argument

        # Save the extracted text for later retrieval
        save_last_extracted_text(text)

        return render_template('result.html', text=text)


def make_unique_filepath(filepath):
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{ext}"
        counter += 1
    return filepath


def extract_text(filepath):
    img = Image.open(filepath)
    text = pytesseract.image_to_string(img)
    return text


def save_last_extracted_text(text):
    with open('last_extracted_text.txt', 'w') as file:
        file.write(text)


def get_last_extracted_text():
    try:
        with open('last_extracted_text.txt', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "No text available"


@app.template_filter('highlight_text')
def highlight_text(text, query):
    if text is not None and query is not None:
        text_str = str(text)
        query_str = str(query)
        return text_str.replace(query_str, f'<mark class="highlight">{query_str}</mark>')
    else:
        return text


def find_text(query):
    extracted_text = get_last_extracted_text().lower()
    if query in extracted_text:
        return highlight_text(extracted_text, query)  # Call highlight_text here
    else:
        return f"No match found for '{query}'"


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    if query:
        result = find_text(query)
        return render_template('result.html', text=result, query=query)
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
