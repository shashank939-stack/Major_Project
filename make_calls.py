import os
import streamlit as st
import pandas as pd
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Set up Streamlit app configuration
st.set_page_config(page_title="InfoCallHub", layout="centered")

# Title of the app
st.title("📞 Info CallHub")

# Instructions
st.write("""
Upload an Excel file containing a list of phone numbers, and initiate automated calls to all numbers.
Ensure that your Excel file has a column named **'phone_number'**.
""")

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '***')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '***')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '***')

# Input for greeting message
greeting_message = st.text_area("📄 Greeting Message", "Hello! This is a test call from InfoCallHub.")

# File uploader
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

def initiate_calls(df):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for number in df['phone_number']:
        try:
            # TwiML to keep the call active and send user input to the Flask server
            twiml = (
                f'<Response>'
                f'<Say>{greeting_message}</Say>'
                f'<Gather input="speech" action=" https://9792-14-139-60-2.ngrok-free.app/handle_response" method="POST" language="en-IN" timeout="4">'
                f'<Say>Please say your question after the beep.</Say>'
                f'</Gather>'
                f'<Say>No input received. The call will continue until you hang up.</Say>'
                f'</Response>'
            )

            call = client.calls.create(
                to=number,
                from_=PHONE_NUMBER,
                twiml=twiml,
                #recording=True
                status_callback=' https://5145-122-15-204-67.ngrok-free.app/status_callback',
                status_callback_method='POST'
            )
            st.success(f"Call initiated to {number}. Call SID: {call.sid}")
        except TwilioRestException as e:
            st.error(f"Failed to call {number}. Error: {str(e)}")

if uploaded_file and ACCOUNT_SID and AUTH_TOKEN and PHONE_NUMBER:
    try:  
        df = pd.read_excel(uploaded_file)
        if 'phone_number' not in df.columns:
            st.error("The uploaded Excel file must contain a column named 'phone_number'.")
        else:
            st.success("Phone numbers successfully loaded!")
            st.write("**Phone Numbers:**")
            st.dataframe(df['phone_number'])
            if st.button("📞 Make Calls"):
                initiate_calls(df)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please provide all necessary information and upload the Excel file to proceed.")
