import os
from flask import Flask, render_template, request, jsonify
import ldclient
from ldclient import Context
from ldclient.config import Config
from threading import Lock, Event

# Initialize LaunchDarkly
sdk_key = "sdk-4b99f9dd-14b4-4479-8aef-232c5399ab39"
feature_flag_key = "userTestFlag"

app = Flask(__name__)

# Set up LaunchDarkly client
if not sdk_key:
    raise ValueError("Please set the LAUNCHDARKLY_SDK_KEY environment variable")

ldclient.set_config(Config(sdk_key))

if not ldclient.get().is_initialized():
    raise RuntimeError("SDK failed to initialize. Please check your internet connection and SDK credential.")

context = Context.builder('example-user-key').kind('user').name('Sandy').build()

def is_feature_enabled():
    flag_value = ldclient.get().variation(feature_flag_key, context, False)
    print(f"Feature flag '{feature_flag_key}' is set to: {flag_value}")
    return flag_value

@app.route('/')
def index():
    feature_enabled = is_feature_enabled()
    return render_template('upload.html', feature_enabled=feature_enabled)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    file.save(os.path.join("uploads", file.filename))
    return jsonify({"status": "success", "filename": file.filename})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    response = test(user_input)
    return jsonify({"response": response})

@app.route('/check_flag', methods=['GET'])
def check_flag():
    feature_enabled = is_feature_enabled()
    return jsonify({"feature_enabled": feature_enabled})

def test(text):
    echo_message = f"The {text} is echoing from the test function"
    print(echo_message)
    return echo_message

if __name__ == '__main__':
    app.run(debug=True)
