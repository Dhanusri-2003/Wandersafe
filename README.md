# Wandersafe
WanderSafe – Real-Time Location-Based Alert System
Step-by-Step Installation and Setup Guide
This document guides you through the process of installing and running the WanderSafe project on your local machine.
1. Prerequisites
Ensure you have the following installed on your system:
- Python 3.8 or higher (https://www.python.org/downloads/)
- pip (Python package installer)
- Git (optional, for cloning from GitHub)
2. Download the Project Source Code
Option 1: Clone from GitHub
    git clone https://github.com/Dhanusri-2003/Wandersafe.git
    cd wandersafe

Option 2: Download ZIP
    - Visit the shared Google Drive or GitHub link.
    - Download and extract the folder.
    - Open the folder in your terminal or code editor.

3. Install Required Packages
Install required Python libraries using pip:
    pip install flask tinydb twilio geopy pyttsx3

4. Configure Twilio
Create a free Twilio account (https://www.twilio.com/).
Get the Account SID, Auth Token, and Twilio Number.
Create a .env file in the root directory and add:
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_number




5.Project Folder Structure
wandersafe/
├── app.py                    # Main Flask application
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── setting.html
│   └── index.html              # Map interface using Leaflet
├── static/
│   ├── css/
│   │   └── style.css         # Basic style
├── database/
│   └── users.json            
6. Run the Flask Server
Start your application by running:
    python app.py

You should see output like:
    Running on http://127.0.0.1:5000/

7. Open the App in Browser
Visit http://127.0.0.1:5000/ in your web browser to use the app:
- Sign up / Login
- Choose destination
- Receive alerts when near
- Use emergency alert button


