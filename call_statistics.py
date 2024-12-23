import streamlit as st
import matplotlib.pyplot as plt
from twilio.rest import Client
# Your Twilio account SID and Auth Token
account_sid = '**'
auth_token = '**'
client = Client(account_sid, auth_token)
def get_calls():
    return client.calls.list()

def analyze_calls(calls):
    status_counts = {
        'completed': 0,
        'busy': 0,
        'failed': 0,
        'no-answer': 0,
        'other': 0
    }
    
    for call in calls:
        status = call.status
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts['other'] += 1
    
    return status_counts

# Streamlit app
st.title('InfoCallHub Statistics')

# Fetch and analyze call data
calls = get_calls()
status_counts = analyze_calls(calls)

# Display the statistics
st.write("Call Status Counts:")
st.write(status_counts)

# Plotting the bar chart
fig, ax = plt.subplots(1, 2, figsize=(14, 7))  # Create a figure with two subplots

# Bar chart
ax[0].bar(status_counts.keys(), status_counts.values(), color='skyblue')
ax[0].set_xlabel('Call Status')
ax[0].set_ylabel('Number of Calls')
ax[0].set_title('Twilio Call Statuses (Bar Chart)')

# Pie chart
sizes = status_counts.values()
labels = status_counts.keys()
colors = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen', 'lightgrey']
ax[1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
ax[1].set_title('Twilio Call Statuses (Pie Chart)')

# Show the plots in Streamlit
st.pyplot(fig)
