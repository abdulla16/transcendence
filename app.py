import boto3
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename

from chunk_and_embedd import embed_text_chunks

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'json'}
app.secret_key = 'supersecretkey'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def test(text, model_id):
    import markdown
    kb_id = 'IX9OJRTSSW'
    model_arn = f'arn:aws:bedrock:us-west-2::foundation-model/{model_id[1]}'
    response = ask_bedrock_llm_with_knowledge_base(text, model_arn, kb_id)
    generated_text = response['output']['text']
    citations = response["citations"]
    contexts = []
    for citation in citations:
        retrievedReferences = citation["retrievedReferences"]
        for reference in retrievedReferences:
            contexts.append(reference["content"]["text"])
    return markdown.markdown(generated_text)



@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    user = 'abdul'
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(user, filename))
        embed_text_chunks(user)
        return redirect(url_for('chat'))

def ask_bedrock_llm_with_knowledge_base(query: str, model_arn: str, kb_id: str) -> str:
    bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", region_name='us-west-2')
    response = bedrock_agent_runtime_client.retrieve_and_generate(
        input={
            'text': query
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': model_arn
            }
        },
    )

    return response


@app.route('/send_message', methods=['POST'])
def send_message():
    claude_model_ids = [["Claude 2.1", "anthropic.claude-v2:1"], ["Claude Instant", "anthropic.claude-instant-v1"]]
    selected_model_id = claude_model_ids[1]
    user_message = request.form.get('message', '')
    if user_message:
        response_text = test(user_message, selected_model_id)  # Call the test function
        response = {
            'user': user_message,
            'assistant': response_text
        }
        return jsonify(response)
    return jsonify({'error': 'No message received'}), 400


if __name__ == '__main__':
    app.run(debug=True)
