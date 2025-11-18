#import the required libraries(for routing, templates, forms, streaming and ollama)
from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context
import ollama

app = Flask(__name__) #create a flask app to handle the requests

#defined the form for username and password (not secure for public use yet)
USERNAME = "admin"
PASSWORD = "admin"

#LOGIN ROUTE
@app.route("/", methods=["GET", "POST"]) #creating the main route for the login
def login():
    if request.method == 'POST': #when the form is submitted
        username = request.form.get("username") #get username from form
        password = request.form.get("password") #get password from form

        #checking if credentials are correct
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("welcome")) #if the credentials are correct direct to welcome page
        else:
            return render_template("login.html",
                                   error="Invalid username or password") #if credentials are incorrect return to log in
    return render_template("login.html") #if the request is GET(just opening the page) show login page

#WELCOME PAGE ROUTE
@app.route("/welcome") #creating the main route for the welcome page
def welcome():
    return render_template("welcome.html") #show welcome page

#CHAT PAGE ROUTE FOR THE LIST OF MODELS
@app.route("/chat", methods=["GET"]) #creating the main route for the chat page and model list
def chat():
    models = ollama.list()["models"] #get all installed ollama models
    model_names = [m.model for m in models] #extract model names
    return render_template("chat.html", models=model_names) #show chat page and forward list of model names to html template

#STREAMING CHAT API ROUTE AND BACKEND
@app.route("/api/stream-chat", methods=["POST"]) #api endpoint for streaming chat
def api_stream_chat(): #function that handles streamed model response
    data = request.get_json() #reads the json payload from request
    user_message = data.get("message", "") #get user message
    model = data.get("model", "gemma3:4b") #get model name or use default
    history = data.get("history", []) #extract previous chat history
    messages = history + [{"role": "user", "content": user_message}] #builds a full convo including the new user messages

    def generate(): #generates function for streaming model tokens
            stream = ollama.chat(model=model, messages=messages, stream=True) #calls ollama in streaming mode
            for chunk in stream: #iterates over streamed chunks
                if "message" in chunk: #makes sure chunk contains message content
                    token = chunk["message"].get("content", "") #extracts token text
                    if token: #if the text exists
                        yield token #send it imediately to the user
    return Response(stream_with_context(generate()), mimetype="text/plain") #returns streamed text response with correct mime type

#activating the server
if __name__ == "__main__": #run the app only when this file is executed
    app.run(debug=True) #enable the debug mode
