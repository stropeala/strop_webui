# Import Flask tools
from flask import (
    Blueprint,              # Used to create modular route groups
    render_template,        # Renders HTML templates
    request,                # Lets us read incoming JSON/form data
    redirect,
    url_for,
    Response,               # Used to send streaming HTTP responses
    stream_with_context     # Ensures streaming cooperates with Flask context
)


# Import login protection so only logged-in users can chat
from flask_login import login_required


# Import Ollama library
import ollama


# Create a Blueprint named chat for all chat-related routes
chat = Blueprint('chat', __name__)


#------------ HELPER FUNCTIONS -------------#


def get_installed_models():

    # Retrieves a list of models installed in the user's Ollama environment
    model_info = ollama.list().get('models', [])
    return [model.model for model in model_info]      # Return only the model name strings


def add_to_conversation_memory(conversation_memory, user_message):

    # Adds the user's latest message to the conversation memory list
    # conversation_memory is a list of dicts like:
    #    {'role': 'user', 'content': 'Hello'}
    new_entry = {'role': 'user', 'content': user_message}
    return conversation_memory + [new_entry]               # Return new conversation list


def stream_model_reply(model_name, conversation_memory):

    # This function yields text chunks as they arrive so the frontend can display the reply live
    # Ask Ollama to start a chat session with the selected model
    # stream=True tells Ollama to send partial tokens instead of waiting for full response
    stream = ollama.chat(
        model=model_name,
        messages=conversation_memory,
        stream=True,
    )


    # Iterate through every streaming chunk sent by Ollama
    for chunk in stream:
        message = chunk.get('message', {})           # Extract message dict
        token = message.get('content', '')           # Extract the generated text

        if token:
            yield token                              # Send token piece to client immediately


#------------ CHAT PAGE -------------#


@chat.route('/chat', methods=['GET'])
@login_required
def chat_page():

    models = get_installed_models()                  # Get available local Ollama models
    return render_template('chat.html', models=models)


@chat.route('/api/stream-chat', methods=['POST'])
@login_required
def streaming_chat_api():

    # Receives:
    #   - A user's message
    #   - The model name
    #   - The existing conversation memory
    #
    # Returns:
    #   - A streaming HTTP response with model-generated tokens

    # JSON payload from frontend
    data = request.get_json()
    user_message = data.get('message', '')           # User's new message string
    model_name = data.get('model', '')               # Model to use
    conversation_memory = data.get('memory', [])     # Previous conversation list


    # Add user's message to conversation buffer
    conversation_memory = add_to_conversation_memory(conversation_memory, user_message)


    # Stream model response back to browser using Response + generator
    return Response(
        stream_with_context(
            stream_model_reply(model_name, conversation_memory)
        ),
        mimetype='text/plain',                       # Plain text chunks streamed dynamically
    )