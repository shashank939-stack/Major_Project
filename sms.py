import os
import streamlit as st
import pandas as pd
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Set up Streamlit app configuration
st.set_page_config(page_title="Bulk SMS Sender", layout="centered")

# Title of the app
st.title("📱 Bulk SMS Sender")

# Instructions
st.write("""
Upload an Excel file containing a list of phone numbers, and send SMS messages to all numbers.
Ensure that your Excel file has a column named **'phone_number'**.
""")

# Retrieve Twilio credentials from environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '***')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '***')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '***')

# Input for SMS message
message_body = st.text_area("📄 Message Body", "Hello! This is a test message from InfoCallHub.")

# File uploader
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

def format_phone_number(number):
    # Ensure the phone number is a string and starts with '+'
    number_str = str(number)
    if not number_str.startswith('+'):
        number_str = f'+{number_str}'
    return number_str

def send_sms(df):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for number in df['phone_number']:
        formatted_number = format_phone_number(number)
        try:
            # Send SMS
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=formatted_number
            )
            st.success(f"Message sent to {formatted_number}. Message SID: {message.sid}")
        except TwilioRestException as e:
            st.error(f"Failed to send message to {formatted_number}. Error: {str(e)}")

if uploaded_file and ACCOUNT_SID and AUTH_TOKEN and TWILIO_PHONE_NUMBER:
    try:
        df = pd.read_excel(uploaded_file)
        if 'phone_number' not in df.columns:
            st.error("The uploaded Excel file must contain a column named 'phone_number'.")
        else:
            df['phone_number'] = df['phone_number'].astype(str)  # Ensure all phone numbers are treated as strings
            st.success("Phone numbers successfully loaded!")
            st.write("**Phone Numbers:**")
            st.dataframe(df['phone_number'])
            if st.button("📤 Send SMS"):
                send_sms(df)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please provide all necessary information and upload the Excel file to proceed.")
