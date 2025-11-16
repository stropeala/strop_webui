#import the required libraries
from flask import Flask, render_template, request, redirect, url_for
import ollama
app = Flask(__name__) #create a Flask app to handle the requests

#defined the form for username and password
USERNAME = "admin"
PASSWORD = "admin"

#LOGIN PAGE
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

@app.route("/welcome") #creating the main route for the welcome page
def welcome():
    return render_template("welcome.html") #show welcome page

@app.route("/chat", methods=["GET", "POST"]) #creating the main route for the chat page
def chat():
    user_input = "" #empty user input so page loads without errors
    bot_reply = "" #empty bot reply for the same reason

    if request.method == "POST": #if user submits a mesage
        user_input = request.form["user_input"] #get user input from this form
        bot_reply = ollama_response(user_input) #sen it to ollama model to get a reply
    #render the chat page and sens these parameters to html
    return render_template("chat.html", user_input=user_input, bot_reply=bot_reply)

def ollama_response(user_input):
    #send the user input to ollama model
    response = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": user_input}])
    print(response) #print the response

    #try to return the ai reply
    try:
        return response.message.content #correct acces pattern
    except AttributeError:
        return "Oops, something went wrong." #fallback if there is no .message or no .content

#Activating the server
if __name__ == "__main__": #run the app only when this file is executed
    app.run(debug=True) #enable the debug mode
