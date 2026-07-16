# IMPORTS

#import json
from flask import Flask, render_template, request, jsonify
import os
import time

# VARIABLES

app = Flask(__name__)

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
DB_USER = os.environ.get("ORACLE_DB_USER")
DB_PASSWORD = os.environ.get("ORACLE_DB_PASSWORD")
DB_DSN = os.environ.get("ORACLE_DB_DSN")

user_input = ""
user_input_words = []
chatbot_output = ""

# PAGES

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/chat')
def chat():
    data = request.get_json()
    # user_message = ### IMPLEMENT ###
    return jsonify({'test response': "this is a test response"})

# FUNCTIONS

def print_debug_header():
    print("test")

def send_greeting():
    # INITIALIZE SOME THINGS?
    # GENERIC GREETING
    pass

def receive_user_message():
    # CALLED ONCE AN INPUT IS DETECTED
    # STORE IN PROGRAM
    # FILTER FOR VALID MESSAGE
    # SPLIT INTO INDIVIDUAL WORDS
    pass

def get_language_pattern():
    # REQUEST LANGUAGE PATTERN FOR EVERY WORD IF IN TABLE, USE "IN", "AT", AND "FOR" TO DETECT A LOCATION AND TIME
    # RECEIVE LANGUAGE PATTERN, STORE TO PROGRAM WITH PLACEHOLDERS
    # STORE LOCATION LATITUDE AND LONGITUDE TO PROGRAM
    pass

def inform_user_await_response():
    # INFORM USER THAT THE CHATBOT IS AWAITING WEATHER DATA
    pass

def get_weather_data():
    # SEND REQUEST TO OPENWEATHER API WITH STORED LATITUDE AND LONGITUDE
    # RECEIVE DATA AND MAP RESPONSE TO WEATHER VALUES
    pass

def output_response():
    # SEND LANGUAGE PATTERN WITH WEATHER DATA FILLED IN FOR PLACEHOLDERS
    # STORE IN PROGRAM
    pass

def log_user_interaction():
    # STORE MOST RECENT USER INPUT AND MOST RECENT CHATBOT OUTPUT STORED IN PROGRAM INTO DATABASE
    pass

# MAIN PROGRAM

if __name__ == "__main__":
    print("Program started.")
    app.run(debug=True)
