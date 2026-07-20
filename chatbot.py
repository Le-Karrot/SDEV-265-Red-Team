# IMPORTS

from flask import Flask, render_template, request, jsonify
import os, oracledb, requests

# VARIABLES

app = Flask(__name__)

#OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
ORACLEDB_USER = os.environ.get("ORACLE_DB_USER")
ORACLEDB_PASSWORD = os.environ.get("ORACLE_DB_PASSWORD")
ORACLEDB_DSN = os.environ.get("ORACLE_DB_DSN")

# FUNCTIONS

def send_greeting():
    # GENERIC GREETING
    return "Hello! I'm Meteor, a virtual chatbot here to give you accurate weather information!"

def receive_user_message(raw_text):
    # RECEIVE AND CLEAN USER MESSAGE
    print("".join(filter(lambda char: char.isalnum() or char.isspace(), raw_text)))
    return "".join(filter(lambda char: char.isalnum() or char.isspace(), raw_text))

def get_response_template_and_city_coordinates(clean_message):
    # LOCAL TESTING
    trigger_words = {
        'temperature': "The temperature is {temp}°F.",
        'feel': "The air temperature index is {feels_like}°F",
        'humidity': "The humidity is {humidity}%.",
        'wind': "The wind speed is {wind}mph.",
        'weather': ""
    }
    locations = {'indianapolis': ("IN", 39.791000, -86.148003, 1)}
    
    user_input_words = []
    input_location = ""
    
    response_template = ""
    city_latitude = 0
    city_longitude = 0

    # REQUEST LANGUAGE PATTERN FOR EVERY WORD IF IN TABLE, USE "IN" AND "AT" TO DETECT A LOCATION AND TIME
    user_input_words = [word.lower() for word in clean_message.split()]
    print("DEBUG:", user_input_words)

    # RETRIEVE LOCATION (3 word -> 2 word -> 1 word)
    num_words = len(user_input_words)
    for n in range(3, 0, -1):
        for i in range(num_words - n + 1):
            phrase = " ".join(user_input_words[i:i+n])
            if input_location == "" and phrase in locations:
                input_location = phrase
                city_latitude, city_longitude = locations[input_location][1:3]
                break
        if input_location != "":
            break
    
    # Begin response template
    response_template = "In " + input_location.title() + " right now:" # POTENTIALLY IMPLEMENT A SECOND OPTION FOR TIME BASED
    
    # Append language pattern to response template for every trigger word
    for word in user_input_words:
        if word in trigger_words:
            response_template += "\n- " + trigger_words.get(word)
        elif word == "weather":
            response_template = "Right now in " + input_location.title() + ", there FINISH IMPLEMENTING FORECAST"
            break
    
    # CONNECT TO TEST FOR LOCATION IN TABLE
    """
    try:
        print("Attempting to connect to Oracle FreeSQL...")

        connection = oracledb.connect(
            user=ORACLEDB_USER,
            password=ORACLEDB_PASSWORD,
            dsn=ORACLEDB_DSN
        )

        print("Success... Database is connected and online.")

        cursor = connection.cursor()
        #cursor.execute("")
        #result = cursor.fetchone()
        #print(f"Database Response: {result[0]}")

        cursor.close()
        connection.close()
        print("Connection closed safely.")

    except Exception as e:
        print(f"Connection Failed!\nError details: {e}")

    """
    return response_template, city_latitude, city_longitude

""" DOES NOTHING USE JAVASCRIPT
def inform_user_await_response():
    # INFORM USER THAT THE CHATBOT IS AWAITING WEATHER DATA
    message_await = "One moment while I gather that information for you..."
    print(message_await)
"""
def get_weather_data(lat, long):
    # SEND REQUEST TO OPENWEATHER API WITH STORED LATITUDE AND LONGITUDE
    # RECEIVE DATA AND MAP RESPONSE TO WEATHER VALUES
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={OPENWEATHER_API_KEY}&units=imperial"
    
    try:
        response = requests.get(api_url)
        # Raise exception if fails
        response.raise_for_status()
        
        data = response.json()
        
        print("\nDEBUG: ", data)

        weather_metrics = {
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'wind': data['wind']['speed'],
            'description': data['weather'][0]['description']
        }
        
        return weather_metrics

    except requests.exceptions.RequestException as e:
        print(f"Weather API Call Failed: {e}")
        return None

def output_response(response_template, weather_data):
    # SEND LANGUAGE PATTERN WITH WEATHER DATA FILLED IN FOR PLACEHOLDERS
    if not weather_data or not response_template:
        return "I'm sorry, I was unable to retrieve weather data for that request."
    
    try:
        # Round or format different data types
        formatted_weather = {
            'temp': round(weather_data.get('temp', 0)),
            'feels_like': round(weather_data.get('feels_like', 0)),
            'humidity': weather_data.get('humidity', 0),
            'wind': round(weather_data.get('wind', 0)),
            'description': weather_data.get('description', '')
        }

        # Inject weather data into all matching placeholders
        return response_template.format_map(formatted_weather)

    except KeyError as e:
        print(f"Key Error: Missing key {e}.")
        return response_template

def log_user_interaction(user_input, chatbot_output):
    # STORE MOST RECENT USER INPUT AND MOST RECENT CHATBOT OUTPUT STORED IN PROGRAM INTO DATABASE
    pass

# PAGES

@app.route('/')
def home_page():
    return render_template('index.html', greeting=send_greeting())

@app.route('/chat', methods=['POST'])
def chat():
    #data = request.get_json()
    #user_input = data.get('message', '')

    user_input = "What is the temperature, humidity, and wind in Indianapolis right now?" # TEST VALUE

    clean_message = receive_user_message(user_input)
    response_template, lat, long = get_response_template_and_city_coordinates(clean_message)
    print(
        "DEBUG:", 
        f"\nRESPONSE_TEMPLATE: {response_template}\n",
        f"LATITUDE: {lat}",
        f"LONGITUDE: {long}"
    )
    weather_data = get_weather_data(lat, long)
    print("DEBUG:", weather_data)
    
    chatbot_output = output_response(response_template, weather_data)
    print("\nDEBUG:\n", chatbot_output)
    #log_user_interaction()

    return jsonify({'test response': "this is a test response"})

# MAIN PROGRAM

if __name__ == "__main__":
    print("Program started.")
    app.run(debug=True)
