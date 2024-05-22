from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
#realy good

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def test(text):
    print(f"The '{text}' is echoing from the test function")
    return f"The '{text}' is echoing from the test function"

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('chat'))

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('message', '')
    if user_message:
        response_text = test(user_message)  # Call the test function
        response = {
            'user': user_message,
            'assistant': response_text
        }
        return jsonify(response)
    return jsonify({'error': 'No message received'}), 400

if __name__ == '__main__':
    app.run(debug=True)
