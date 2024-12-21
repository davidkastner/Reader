import os
import requests
import pandas as pd
import datetime
import plotly.express as px
import streamlit as st

# Constants
API_URL = "https://readwise.io/api/v3/list/"

# Fetch the Readwise token from environment variables
TOKEN = os.getenv("READWISE_TOKEN")
if not TOKEN:
    st.error("Readwise token not found. Please set it as an environment variable in your Streamlit Cloud settings.")
    st.stop()

# Helper Function to Fetch Data
def fetch_readwise_data():
    headers = {"Authorization": f"Token {TOKEN}"}
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

# Preprocessing Function
def process_data(data):
    if not data:
        return pd.DataFrame(columns=["date", "pages"])

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
st.write("Track your reading progress over time with data from your Readwise Reader.")

if st.button("Update"):
    st.write("Fetching your reading data...")
    raw_data = fetch_readwise_data()
    
    if raw_data:
        st.write("Processing data...")
        data = process_data(raw_data)

        if not data.empty:
            st.success("Data loaded successfully!")

            # Plotting
            fig = px.line(
                data,
                x="date",
                y="pages",
                title="Pages Read Per Day",
                labels={"date": "Date", "pages": "Pages Read"},
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Pages",
                template="plotly_white"
            )
            st.plotly_chart(fig)
        else:
            st.warning("No reading data available to display.")
    else:
        st.error("Failed to retrieve or process data.")

st.write("Click the 'Update' button to refresh your reading data.")
