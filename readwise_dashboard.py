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

# Data Processing for Highlights and Notes
def process_highlights_and_notes(data):
    if not data:
        return pd.DataFrame(columns=["date", "type", "count"])

    highlights_dates = []
    notes_dates = []

    for doc in data:
        updated_at = doc.get("updated_at")
        if updated_at:
            date = updated_at[:10]  # Extract the date
            if doc.get("parent_id"):  # It's a highlight if it has a parent_id
                highlights_dates.append(date)
            if doc.get("notes"):  # It's a note if it has non-empty notes
                notes_dates.append(date)

    # Count highlights and notes by date
    highlights_df = pd.DataFrame({"date": highlights_dates})
    notes_df = pd.DataFrame({"date": notes_dates})

    highlights_counts = highlights_df.groupby("date").size().reset_index(name="count")
    highlights_counts["type"] = "Highlights"

    notes_counts = notes_df.groupby("date").size().reset_index(name="count")
    notes_counts["type"] = "Notes"

    return pd.concat([highlights_counts, notes_counts], ignore_index=True)

# Plotting Function
def plot_highlights_and_notes(data):
    if data.empty:
        st.write("No data available to plot.")
        return

    fig = px.line(
        data,
        x="date",
        y="count",
        color="type",
        title="Highlights and Notes Over Time",
        labels={"date": "Date", "count": "Count", "type": "Type"},
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# Statistics Display Function
def display_statistics(data):
    if data.empty:
        st.write("No statistics to display as no data is available.")
        return

    total_highlights = data[data["type"] == "Highlights"]["count"].sum()
    total_notes = data[data["type"] == "Notes"]["count"].sum()

    st.subheader("Statistics")
    st.write(f"**Total Highlights:** {total_highlights}")
    st.write(f"**Total Notes:** {total_notes}")

# Main Function to Run the App
def main():
    st.set_page_config(page_title="Readwise Reader Dashboard", layout="wide")
    st.title("Reader Dashboard")

    raw_data = fetch_readwise_data()
    data = process_highlights_and_notes(raw_data)

    if not data.empty:
        st.success("Data loaded successfully!")

        # Convert date to datetime for filtering
        data["date"] = pd.to_datetime(data["date"])

        # Date range slider
        min_date = data["date"].min().date()
        max_date = data["date"].max().date()

        if min_date == max_date:
            st.warning(f"All data is from a single day: {min_date}. Showing all data.")
            filtered_data = data
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

        plot_highlights_and_notes(filtered_data)
        display_statistics(filtered_data)
    else:
        st.warning("No data available to display.")
        plot_highlights_and_notes(pd.DataFrame(columns=["date", "type", "count"]))

# Run the App
if __name__ == "__main__":
    main()
