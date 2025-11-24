from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    Response,
    stream_with_context
)
from flask_login import login_required
import ollama


chat = Blueprint('chat', __name__)


# ------------------- Helper Functions --------------------


def get_installed_models():
    model_info = ollama.list().get('models', [])
    return [model.model for model in model_info]

def add_to_conversation_memory(conversation_memory, user_message):
    new_entry = {'role': 'user', 'content': user_message}
    return conversation_memory + [new_entry]

def stream_model_reply(model_name, conversation_memory):
    stream = ollama.chat(
        model=model_name,
        messages=conversation_memory,
        stream=True,
    )

    for chunk in stream:
        message = chunk.get('message', {})
        token = message.get('content', '')

        if token:
            yield token


# ------------------- Routes --------------------


@chat.route('/chat', methods=['GET'])
@login_required
def chat_page():
    models = get_installed_models()
    return render_template('chat.html', models=models)

@chat.route('/api/stream-chat', methods=['POST'])
@login_required
def streaming_chat_api():
    data = request.get_json()
    user_message = data.get('message', '')
    model_name = data.get('model', '')
    conversation_memory = data.get('memory', [])

    conversation_memory = add_to_conversation_memory(conversation_memory, user_message)

    return Response(
        stream_with_context(
            stream_model_reply(model_name, conversation_memory)
        ),
        mimetype='text/plain',
    )
