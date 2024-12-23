import os
import streamlit as st
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from requests.auth import HTTPBasicAuth
import requests
# Set up Streamlit app configuration
st.set_page_config(page_title="InfoCallHub", layout="centered")

# Title of the app
st.title("📞 Info CallHub")
st.title("Recordings")
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '***')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '***')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '***')

client = Client(ACCOUNT_SID, AUTH_TOKEN)
def get_recordings():
    return client.recordings.list()



# Fetch recordings
recordings = get_recordings()

if recordings:
    for recording in recordings:
        st.write(f"Recording SID: {recording.sid}")
        st.write(f"Date Created: {recording.date_created}")
        st.write(f"Duration: {recording.duration} seconds")

        # Use the media URL provided by Twilio to access the recording
        media_url = recording.uri.replace('.json', '.mp3')
        # Construct full URL
        recording_url = f'https://api.twilio.com{media_url}'

        # Authenticate and fetch the content
        response = requests.get(recording_url, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))
        
        # Check if the request was successful
        if response.status_code == 200:
            st.audio(response.content, format='audio/mp3')
        else:
            st.write(f"Failed to load recording: {response.status_code}")
else:
    st.write("No recordings found.")