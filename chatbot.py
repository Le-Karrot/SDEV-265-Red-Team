# IMPORTS

from flask import Flask, render_template, request, jsonify
import os, oracledb, requests

try:
    oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_0")
except Exception:
    pass

# VARIABLES

app = Flask(__name__)

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
ORACLEDB_USER = os.environ.get("ORACLEDB_USER")
ORACLEDB_PASSWORD = os.environ.get("ORACLEDB_PASSWORD")
ORACLEDB_DSN = os.environ.get("ORACLEDB_DSN")


# FUNCTIONS

def send_greeting():
    # Generic greeting
    return "Hello! I'm Meteor, a virtual chatbot here to give you accurate weather information!"

def receive_user_message(raw_text):
    # Input validation
    if not raw_text or not isinstance(raw_text, str):
        return ""
    
    # Receive and clean user message, 500 char limit
    clean = "".join(filter(lambda char: char.isalnum() or char.isspace(), raw_text[:500]))
    return clean.strip()

def get_response_template_and_city_coordinates(clean_message, target_city = None, original_query = None):
    # Local trigger word and language pattern dictionary
    trigger_words = {
        'temperature': "The temperature is {temp}°F.",
        'index': "The heat index is {feels_like}°F",
        'chill': "The wind chill is {feels_like}°F",
        'humidity': "The humidity is {humidity}%.",
        'wind': "The wind speed is {wind}mph.",
        'cloud': "The cloud cover is {cloud_cover}%",
        'visibility': "The visibility is {visibility}mi"
    }

    # If resolving a duplicate, parse words from original_query instead
    text_to_parse = original_query if original_query else clean_message
    # Split user message into individual words
    user_input_words = [word.lower() for word in text_to_parse.split()]
    print("DEBUG:", user_input_words)

    # Variables to be changed
    input_location = ""
    city_latitude = 0
    city_longitude = 0

    # Connect to request location data from table
    try:
        print("Attempting to connect to Oracle FreeSQL...")

        with oracledb.connect(
            user=ORACLEDB_USER,
            password=ORACLEDB_PASSWORD,
            dsn=ORACLEDB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                # Check if resolving duplicate city
                if target_city:
                    sql = "SELECT city_name, state_abbr, latitude, longitude FROM preset_cities WHERE LOWER(city_name) = :1 AND (LOWER(state_abbr) = :2)"
                    # Query for city with state specified
                    cursor.execute(sql, [target_city.lower(), clean_message.strip().lower()])
                    results = cursor.fetchall()

                    if len(results) >= 1:
                        city_name, state, city_latitude, city_longitude = results[0]
                        input_location = city_name
                    else:
                        return f"Sorry, I couldn't find '{target_city.title()}' in '{clean_message.upper()}'.", 0, 0, None, False
                # Otherwise use normal slices
                else: 
                    # Retrive location from slices of words with descending word count (3 word -> 2 word -> 1 word)
                    num_words = len(user_input_words)
                    for n in range(3, 0, -1):
                        for i in range(num_words - n + 1):
                            phrase = " ".join(user_input_words[i:i+n])

                            # Query for current slice
                            sql = "SELECT city_name, state_abbr, latitude, longitude FROM preset_cities WHERE LOWER(city_name) = :1"
                            cursor.execute(sql, [phrase])
                            results = cursor.fetchall()
                            
                            # City list results length detection
                            if len(results) == 1:
                                city_name, state, city_latitude, city_longitude = results[0]
                                input_location = city_name
                                print(f"Found match: {city_name}, {state} (Lat: {city_latitude}, Lon: {city_longitude})")
                                break
                            elif len(results) > 1:
                                available_states = ", ".join([row[1] for row in results])
                                prompt = f"Multiple cities named '{phrase.title()}' were found. What is the state of the city you were referring to? ({available_states})"
                                return prompt, 0, 0, phrase, True
                            
                        if input_location != "":
                            break

    except Exception as e:
        print(f"Connection Failed!\nError details: {e}")

    # No city matched in database
    if not input_location:
        return "Sorry, I either couldn't find a specified city in your request, or your chosen city is not currently supported.", 0, 0, None, False

    # Begin response template
    response_template = "In " + input_location.title() + " right now:"
    
    # Append language pattern to response template for every trigger word
    for word in user_input_words:
        if word in trigger_words:
            response_template += "\n- " + trigger_words.get(word)
        elif word == "weather":
            response_template = (
                "Right now in " + input_location.title() + ", it is {description} "
                + "with a temperature of {temp}°F, but feels like {feels_like}°F. "
                + "There is a wind speed of {wind}mph and a humidity of {humidity}%."
            )
            break

    return response_template, city_latitude, city_longitude, None, False


def get_weather_data(lat, long):
    # Send request to OpenWeather API with latitude and longitude
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={OPENWEATHER_API_KEY}&units=imperial"
    
    try:
        response = requests.get(api_url)
        # Raise exception if fails
        response.raise_for_status()
        
        data = response.json()
        
        print("\nDEBUG: ", data)
        # Receive data and map JSON response to placeholders
        weather_metrics = {
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'wind': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'cloud_cover': data['clouds']['all'],
            'visibility': data['visibility']
        }
        
        return weather_metrics

    except requests.exceptions.RequestException as e:
        print(f"Weather API Call Failed: {e}")
        return None

def output_response(response_template, weather_data):
    # Send response template with weather data filled in for placeholders
    if not weather_data or not response_template:
        return "I'm sorry, I was unable to retrieve weather data for that request."
    
    try:
        # Round or format different data types
        raw_desc = weather_data.get('description', '')
        clean_desc = (
            "cloudy" if "cloud" in raw_desc else
            "rainy"  if "rain" in raw_desc or "drizzle" in raw_desc else
            "snowy"  if "snow" in raw_desc else
            "sunny"  if "clear" in raw_desc else
            raw_desc
        )

        formatted_weather = {
            'temp': round(weather_data.get('temp', 0)),
            'feels_like': round(weather_data.get('feels_like', 0)),
            'humidity': weather_data.get('humidity', 0),
            'wind': round(weather_data.get('wind', 0)),
            'description': clean_desc,
            'cloud_cover': round(weather_data.get('cloud_cover', 0)),
            'visibility': round(weather_data.get('visibility', 0)/1.609)
        }

        # Place weather data into all matching placeholders
        return response_template.format_map(formatted_weather)

    except KeyError as e:
        print(f"Key Error: Missing key {e}.")
        return response_template

# PAGES

@app.route('/')
def home_page():
    return render_template('index.html', greeting=send_greeting())

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # Validate that data exists
    if not data or 'message' not in data:
        return jsonify({'response': "Invalid format.", 'is_duplicate': False}), 400
    
    user_input = data.get('message', '')
    target_city = data.get('target_city', None)
    original_query = data.get('original_query', None)

    clean_message = receive_user_message(user_input)
    response_template, lat, long, duplicate_city, is_duplicate = get_response_template_and_city_coordinates(
        clean_message, target_city, original_query
    )
    if is_duplicate:
        return jsonify({'response': response_template, 'is_duplicate': True, 'city_name': duplicate_city})
    if lat == 0 and long == 0:
        return jsonify({'response': response_template, 'is_duplicate': False})
    
    weather_data = get_weather_data(lat, long)
    chatbot_output = output_response(response_template, weather_data)

    return jsonify({'response': chatbot_output, 'is_duplicate': False})

# MAIN PROGRAM

if __name__ == "__main__":
    print("Program started.")
    app.run(debug=True)
