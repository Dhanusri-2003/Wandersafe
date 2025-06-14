from flask import Flask, render_template,jsonify, request, redirect, url_for, session
from tinydb import TinyDB, Query
from twilio.rest import Client
import os
from flask_cors import CORS
from geopy.geocoders import Nominatim
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)
app.secret_key = 'smarttravelsecret'
CORS(app)


def get_location_name(lat, lon):
    # Initialize the geolocator with a user agent name
    geolocator = Nominatim(user_agent="smart_travel_app")

    # Perform reverse geocoding to get the location address
    location = geolocator.reverse((lat, lon), language='en')

    # Return the address if available, otherwise return "Unknown Location"
    if location:
        return location.address
    else:
        return "Unknown Location"


# Twilio Credentials
ACCOUNT_SID = '**********************************'
AUTH_TOKEN = '*******************************'
TWILIO_PHONE = '***********'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Dynamically get the full path to smart_travel_app/users/users.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DIR = os.path.join(BASE_DIR, 'users')
os.makedirs(USER_DIR, exist_ok=True)  # Creates the 'users' folder if it doesn't exist
USER_FILE_PATH = os.path.join(USER_DIR, 'users.json')

db = TinyDB(USER_FILE_PATH)
User = Query()


@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')
    return redirect('/login')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        user_phone = request.form['userPhone']
        call_phone = request.form['callPhone']

        if db.search(User.username == username):
            return 'Username already exists'
        
        db.insert({
            'name': name,
            'username': username,
            'password': password,
            'userPhone': user_phone,
            'callPhone': call_phone
        })
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.get(User.username == username)

        if user and user['password'] == password:
            session['username'] = username
            return redirect('/')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/send_alert', methods=['POST'])
def send_alert():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get coordinates from the request (sent by JS)
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')

    if not lat or not lon:
        return "Missing latitude or longitude", 400

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return "Invalid coordinates", 400

    # Reverse geocode to get the destination name
    destination_name = get_location_name(lat, lon)

    # Get user info from database
    User = Query()
    user = db.search(User.username == session['username'])[0]
    user_name = user['name']
    user_phone = user['userPhone']
    call_phone = user['callPhone']

    # Create personalized message
    message = f"Hi {user_name}, you are going to reach {destination_name}."

    # Send SMS and call
    send_sms(user_phone, message)
    send_call(call_phone)

    return "Alert Sent!"


def send_sms(to_phone, message):
    """Function to send an SMS using Twilio"""
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE,
        to=to_phone
    )
    print(f"SMS sent to {to_phone}: {message.sid}")
    print("Received /send_alert POST")


def send_call(to_phone):
    """Function to make a phone call using Twilio with default message"""
    call = client.calls.create(
        to=to_phone,
        from_=TWILIO_PHONE,
        url="http://demo.twilio.com/docs/voice.xml"  # Twilio's default voice response
    )
    print(f"Call initiated to {to_phone}: {call.sid}")
    print("Received /send_alert POST")



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return redirect('/login')
    
    user = db.get(User.username == session['username'])

    if request.method == 'POST':
        db.update({
            'name': request.form['name'],
            'userPhone': request.form['userPhone'],
            'callPhone': request.form['callPhone']
        }, User.username == session['username'])
        return redirect('/')
    
    return render_template("settings.html", user=user)

@app.route("/trigger_alert", methods=["POST"])
def trigger_alert():
    try:
        data = request.get_json()
        print("Received data:", data)

        lat = data.get("latitude")
        lon = data.get("longitude")

        if not lat or not lon:
            print("Missing latitude or longitude")
            return jsonify({"error": "Missing coordinates"}), 400

        if 'username' not in session:
            print("Username not in session")
            return jsonify({"error": "User not logged in"}), 401

        # Get user from DB
        User = Query()
        db_user = db.search(User.username == session['username'])
        if not db_user:
            print("User not found in DB")
            return jsonify({"error": "User not found in DB"}), 404

        user = db_user[0]

        # Get location name
        geolocator = Nominatim(user_agent="wander_safe")
        location = geolocator.reverse(f"{lat}, {lon}", language='en')
        place_name = location.address if location else "Unknown location"

        # Compose message
        message = f"🚨 {user['name']} is in {place_name} and has triggered an emergency alert!"

        # Send SMS
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=user['callPhone']
        )
        print("SMS SID:", sms.sid)

        return jsonify({"status": "Alert sent"}), 200

    except Exception as e:
        print("Exception occurred:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)