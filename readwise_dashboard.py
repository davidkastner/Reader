import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px

# Constants
API_URL = "https://readwise.io/api/v3/list/"
TOKEN = st.secrets["READWISE_TOKEN"]  # Fetch the token securely

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
        # Ensure "last_opened_at" and "word_count" exist and are not None
        last_opened_at = doc.get("last_opened_at")
        word_count = doc.get("word_count")

        if last_opened_at and word_count:
            date = last_opened_at[:10]  # Extract the date
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

            # Slider for adjusting the date range
            min_date = data["date"].min()
            max_date = data["date"].max()

            range_percent = st.slider(
                "Adjust Date Range (as % of total days):",
                min_value=0,
                max_value=100,
                value=(0, 100),
                step=1,
            )

            start_idx = int(len(data) * range_percent[0] / 100)
            end_idx = int(len(data) * range_percent[1] / 100)

            filtered_data = data.iloc[start_idx:end_idx]

            # Plotting
            fig = px.line(
                filtered_data,
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
