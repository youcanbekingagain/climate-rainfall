import streamlit as st
import pandas as pd
from query_database import PostgresDataHandler
from plot_functions.indian_map import plot_choropleth_map


def main():
    # Sidebar selections
    granularity = st.sidebar.selectbox("Select granularity:", ["state", "district"])
    frequency = st.sidebar.selectbox(
        "Select frequency:", ["daily", "monthly", "yearly"]
    )
    variable = st.sidebar.selectbox(
        "Select variable to plot:", ["rain", "tmin", "tmax"]
    )

    if frequency == "daily":
        selected_date = st.sidebar.date_input(
            "Select date:",
            pd.to_datetime("2023-01-01"),
            min_value=pd.to_datetime("2018-01-01"),
            max_value=pd.to_datetime("2023-12-31"),
        )
    elif frequency == "monthly":
        selected_year = st.sidebar.selectbox("Select year:", range(2018, 2024))
        selected_month = st.sidebar.selectbox(
            "Select month:",
            [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
        )
        selected_date = pd.to_datetime(f"{selected_year}-{selected_month}-01")
    else:  # yearly
        selected_year = st.sidebar.selectbox("Select year:", range(2018, 2024))
        selected_date = pd.to_datetime(f"{selected_year}-01-01")

    # PostgreSQL connection
    def get_postgres_handler():
        if "data_handler" not in st.session_state:
            st.session_state.data_handler = PostgresDataHandler()
        return st.session_state.data_handler

    # Fetch data based on frequency
    data_handler = get_postgres_handler()
    data = data_handler.query_table(selected_date, frequency)

    # Debugging statement
    st.write("Fetched Data:", data)

    # Plotting
    if data is not None and not data.empty:
        fig = plot_choropleth_map(data, granularity, variable)
        st.plotly_chart(fig)
    else:
        st.write("No data found or an error occurred while querying.")


if __name__ == "__main__":
    main()
