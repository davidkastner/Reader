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
def process_data(data, max_pages):
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
            if pages <= max_pages:  # Filter out excessively high values
                dates.append(date)
                page_counts.append(pages)

    df = pd.DataFrame({"date": dates, "pages": page_counts})
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date").sum().reset_index()
    return df

# Streamlit App
st.set_page_config(page_title="Readwise Reader Dashboard", layout="wide")
st.title("Readwise Reader Dashboard")
st.write("Track your reading progress over time with data from your Readwise Reader.")

# Input box for filtering excessive values
max_pages = st.number_input(
    "Enter the maximum number of pages to allow per day:", value=100, step=10
)

# Fetch and process data automatically on load
st.write("Fetching your reading data...")
raw_data = fetch_readwise_data()

data = process_data(raw_data, max_pages)

if not data.empty:
    st.success("Data loaded successfully!")

    # Date range slider
    min_date = data["date"].min()
    max_date = data["date"].max()

    date_range = st.slider(
        "Select Date Range:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
    )

    filtered_data = data[(data["date"] >= date_range[0]) & (data["date"] <= date_range[1])]

    # Plotting
    fig = px.line(
        filtered_data,
        x="date",
        y="pages",
        title="Pages Read Per Day",
        labels={"date": "Date", "pages": "Pages Read"},
    )
    fig.update_traces(line_color="#EC5A53")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Pages",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Basic statistics
    total_pages = filtered_data["pages"].sum()
    avg_pages = filtered_data["pages"].mean()
    max_pages_day = filtered_data.loc[filtered_data["pages"].idxmax()]

    st.subheader("Statistics")
    st.write(f"**Total Pages Read:** {total_pages:.2f}")
    st.write(f"**Average Pages Per Day:** {avg_pages:.2f}")
    st.write(f"**Highest Pages Read in a Day:** {max_pages_day['pages']:.2f} on {max_pages_day['date'].strftime('%Y-%m-%d')}")
else:
    st.warning("No reading data available to display.")

st.write("Adjust the maximum pages per day or the date range to refine the display.")
