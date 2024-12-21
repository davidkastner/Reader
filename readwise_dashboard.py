import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px

# Constants
API_URL = "https://readwise.io/api/v3/list/"
TOKEN = "Your_Readwise_Access_Token"

# Helper Function to Fetch Data
def fetch_readwise_data():
    headers = {"Authorization": f"Token {TOKEN}"}
    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        st.error("Failed to fetch data. Check your API token or network.")
        return None
    return response.json()["results"]

# Preprocessing Function
def process_data(data):
    dates = []
    page_counts = []

    for doc in data:
        if "last_opened_at" in doc and "word_count" in doc:
            date = doc["last_opened_at"][:10]  # Extract the date
            word_count = doc["word_count"]
            pages = word_count / 250  # Assume 250 words per page
            dates.append(date)
            page_counts.append(pages)

    df = pd.DataFrame({"date": dates, "pages": page_counts})
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date").sum().reset_index()
    return df

# Streamlit App
st.title("Readwise Reader Dashboard")
st.write("Track your reading progress over time.")

if st.button("Update"):
    st.write("Fetching your reading data...")
    raw_data = fetch_readwise_data()
    if raw_data:
        st.write("Processing data...")
        data = process_data(raw_data)
        st.success("Data loaded successfully!")

        # Plotting
        fig = px.line(data, x="date", y="pages", title="Pages Read Per Day")
        fig.update_layout(xaxis_title="Date", yaxis_title="Pages")
        st.plotly_chart(fig)
    else:
        st.error("No data available.")
