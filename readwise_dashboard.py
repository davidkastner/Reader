import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

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

# Data Processing Function
def process_data(data, max_words):
    if not data:
        return pd.DataFrame(columns=["date", "words"])

    dates = []
    word_counts = []

    for doc in data:
        last_opened_at = doc.get("last_opened_at")
        word_count = doc.get("word_count")

        if last_opened_at and word_count:
            date = last_opened_at[:10]  # Extract the date
            if word_count <= max_words:
                dates.append(date)
                word_counts.append(word_count)

    df = pd.DataFrame({"date": dates, "words": word_counts})
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date").sum().reset_index()
    return df

# Plotting Function
def plot_data(filtered_data):
    if filtered_data.empty:
        st.write("No data available to plot.")
        fig = px.line(
            title="Words Read Per Day",
            labels={"date": "Date", "words": "Words Read"},
        )
    else:
        fig = px.line(
            filtered_data,
            x="date",
            y="words",
            title="Words Read Per Day",
            labels={"date": "Date", "words": "Words Read"},
        )
        fig.update_traces(line_color="#EC5A53")
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Words",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# Statistics Display Function
def display_statistics(filtered_data):
    if filtered_data.empty:
        st.write("No statistics to display as no data is available.")
        return

    total_words = filtered_data["words"].sum()
    avg_words = filtered_data["words"].mean()
    max_words_day = filtered_data.loc[filtered_data["words"].idxmax()]

    st.subheader("Statistics")
    st.write(f"**Total Words Read:** {total_words:.0f}")
    st.write(f"**Average Words Per Day:** {avg_words:.0f}")
    st.write(f"**Highest Words Read in a Day:** {max_words_day['words']:.0f} on {max_words_day['date'].strftime('%Y-%m-%d')}")

# Main Function to Run the App
def main():
    st.set_page_config(page_title="Readwise Reader Dashboard", layout="wide")
    st.title("Reader Dashboard")
    st.write("Track your reading progress over time with data from your Readwise Reader.")

    max_words = st.number_input(
        "Enter the maximum number of words to allow per day:", value=25000, step=1000
    )

    st.write("Fetching your reading data...")
    raw_data = fetch_readwise_data()
    data = process_data(raw_data, max_words)

    if not data.empty:
        st.success("Data loaded successfully!")

        # Date range slider with handling for single-date data
        min_date = data["date"].min().date()
        max_date = data["date"].max().date()

        if min_date == max_date:
            st.warning(f"All data is from a single day: {min_date}. Showing all data.")
            filtered_data = data  # No filtering needed
        else:
            date_range = st.slider(
                "Select Date Range:",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
            )

            filtered_data = data[
                (data["date"] >= pd.Timestamp(date_range[0])) & (data["date"] <= pd.Timestamp(date_range[1]))
            ]

        plot_data(filtered_data)
        display_statistics(filtered_data)
    else:
        st.warning("No reading data available to display.")
        plot_data(pd.DataFrame(columns=["date", "words"]))

    st.write("Adjust the maximum words per day or the date range to refine the display.")

# Run the App
if __name__ == "__main__":
    main()
