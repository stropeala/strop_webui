#Import the required libraries
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__) #Create a Flask app to handle the requests

#Defined the username and password for the login
USERNAME = "admin"
PASSWORD = "admin"

@app.route("/", methods=["GET", "POST"]) #Creating the main route for the login
def login():
    if request.method == 'POST': #Authorisation check
        #get data from
        username = request.form.get("username")
        password = request.form.get("password")

        #checking the data
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("welcome")) #if the credentials are correct direct to welcome page
        else:
            return render_template("login.html",
                                   error="Invalid username or password") #if credentials are incorrect return to login
    return render_template("login.html")

@app.route("/welcome") #Creating the main route for the welcome page
def welcome():
    return render_template("welcome.html")

#Activating the server
if __name__ == "__main__":
    app.run(debug=True)
