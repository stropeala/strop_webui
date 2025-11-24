from flask import (
Flask,
render_template,
request,
redirect,
url_for,
Response,
stream_with_context
)
import ollama


app = Flask(__name__)

# Placeholder credentials
USERNAME = "admin"
PASSWORD = "admin"


#------------------- FUNCTIONS --------------------#


# Asks Ollama for all installed models
# Returns a list of model names
def get_installed_models():

    model_info = ollama.list().get("models", [])
    return [model.model for model in model_info]


# Adds the latest user message to the conversation memory
# The memory is managed by the app, not the model
# This returns a new list to the model every time
def add_to_conversation_memory(conversation_memory, user_message):

    new_entry = {"role": "user", "content": user_message}
    return conversation_memory + [new_entry]


# Calls the Ollama model in streaming mode
# The model sends back the response in tiny pieces
# This yields each piece immediately so the browser can display it live
def stream_model_reply(model_name, conversation_memory):

    stream = ollama.chat(
        model = model_name,
        messages = conversation_memory, # Gives the model the full conversation
        stream = True,
    )

    for chunk in stream:
        message = chunk.get("message", {})
        token = message.get("content", "")

        if token:
            yield token


#------------------- LOGIN PAGE (/) --------------------#


@app.route("/", methods = ["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("welcome"))

        return render_template(
            "login_vechi.html",
            error = "Invalid username or password."
        )

    return render_template("login_vechi.html")


#------------------- WELCOME PAGE (/welcome) --------------------#


@app.route("/welcome")
def welcome():

    return render_template("welcome_vechi.html")


#------------------- CHAT PAGE (/chat) --------------------#


@app.route("/chat", methods = ["GET"])
def chat():

    models = get_installed_models()

    return render_template(
        "chat_vechi.html",
        models = models
    )


#------------------- STREAMING CHAT API (/api/stream-chat) --------------------#


@app.route("/api/stream-chat", methods=["POST"])
def streaming_chat_api():

    # Reads json sent from browser
    data = request.get_json()

    # Extracts parts of the request
    user_message = data.get("message", "")
    model_name = data.get("model", "")
    conversation_memory = data.get("memory", []) # Previous "memory"

    # Adds the latest message to "memory"
    conversation_memory = add_to_conversation_memory(conversation_memory, user_message)

    # Streams the model's response back to the browser
    return Response(
        stream_with_context(
            stream_model_reply( model_name, conversation_memory )
        ),
        mimetype = "text/plain",
    )


#------------------- START SERVER --------------------#


if __name__ == "__main__":
    app.run(debug=True)
