import os
from dotenv import load_dotenv
from flask import Flask, jsonify,request, send_from_directory
from coordinates import (get_location_from_google, get_photo, get_photo_reference,
                        get_place_id_from_coordinates, get_location_name,
                        )
from weather2 import get_current_weather, get_five_day_forecast
from flask_cors import CORS 

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

def create_app():
    """
        Summary:
        Creates and configures a Flask application instance.

        Explanation:
        Initializes a Flask application with the provided name and static folder, 

        Args:
        - None

        Returns:
        - Configured Flask application instance.
    """

    app = Flask(__name__, static_folder='static')
    CORS(app)
    return app

app = create_app()

@app.errorhandler(500)
def internal_server_error(e):
    """
        Summary:
        Handles 500 errors by returning a JSON response with the error message.

        Explanation:
        Receives the error message 'e', converts it to a string, and returns a JSON
        response with the error message and status code 500.

        Args:
        - e: The error message.

        Returns:
        - JSON response with the error message and status code 500.
    """

    return jsonify(error=str(e)), 500

@app.errorhandler(404)
def not_found_error(e):
    """
        Summary:
        Handles 404 errors by returning a JSON response with the error message.

        Explanation:
        Receives the error message 'e', converts it to a string, and returns a
        JSON response with the error message and status code 404.

        Args:
        - e: The error message.

        Returns:
        - JSON response with the error message and status code 404.
    """

    return jsonify(error=str(e)), 404

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
        Summary:
        Serves static files or index.html based on the provided path.

        Explanation:
        If the path is not empty and the file exists in the static folder,
        it serves the file. Otherwise, it serves the index.html file.

        Args:
        - path: The path to the static file.

        Returns:
        - The requested static file or index.html.
    """

    if path != "" and os.path.exists(f'{app.static_folder}/{path}'):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    """
        Summary:
        Handles POST request to retrieve weather data based on user-provided location.

        Explanation:
        Retrieves user-provided location data, fetches current weather, forecast, 
        location name, and photo for the location. Returns JSON response with weather
        data and location information.

        Args:
        - None

        Returns:
        - JSON response containing current weather, forecast, photo path, and location information

        Raises:
        - None
    """

    data = request.get_json()
    location = data.get('location')
    if location is None:
        return jsonify(error="No location provided.")
    location_result = get_location_from_google(GOOGLE_API_KEY, location=location)

    if location_result is None:
        return jsonify(error="Unable to retrieve location from Google Geolocation API.")
    latitude, longitude = location_result
    location_name = get_location_name(latitude, longitude)
    place_id = get_place_id_from_coordinates(GOOGLE_API_KEY, latitude, longitude)
    current_weather = get_current_weather(latitude, longitude, OPENWEATHER_API_KEY)
    forecast = get_five_day_forecast(latitude, longitude, OPENWEATHER_API_KEY)
    photo_reference = get_photo_reference(GOOGLE_API_KEY, place_id)
    photo_path = None
    if photo_reference is not None:
        photo_filename = get_photo(photo_reference, GOOGLE_API_KEY)
        photo_path = 'images/photo.jpg' if photo_filename is not None else None
    return jsonify(current_weather=current_weather, forecast=forecast,
                photo_path=photo_path, location=location_name,
                )

@app.route('/weather', methods=['GET'])
def weather():
    """
        Summary:
        Handles GET request to retrieve current weather and forecast data based on user's location.

        Explanation:
        Retrieves user's latitude and longitude, then fetches current weather, forecast, 
        location name, and photo for the location. Returns JSON response with current weather
        and forecast data.
        Args:
        - None

        Returns:
        - JSON response containing current weather and forecast data

        Raises:
        - None
    """

    latitude, longitude = get_location_from_google(GOOGLE_API_KEY)
    if latitude is not None and longitude is not None:
        current_weather = get_current_weather(latitude, longitude, OPENWEATHER_API_KEY)
        forecast = get_five_day_forecast(latitude, longitude, OPENWEATHER_API_KEY)
        place_id = get_place_id_from_coordinates(GOOGLE_API_KEY, latitude, longitude)
        photo_reference = get_photo_reference(GOOGLE_API_KEY, place_id)
        photo_path = get_photo(photo_reference, GOOGLE_API_KEY)
        location_name = get_location_name(latitude, longitude)
        print(photo_path, location_name)
        return jsonify(current_weather=current_weather, forecast=forecast)
    return jsonify(error="Unable to retrieve location from Google Geolocation API.")

if __name__ == "__main__":
    app.run(port=5001)
