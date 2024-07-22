import streamlit as st
import pandas as pd
from query_database import PostgresDataHandler
from plot_functions.indian_map import (
    plot_choropleth_map,
    plot_barchart,
    plot_scatter,
    plot_histogram,
    plot_boxplot,
    plot_heatmap,
    plot_count_chart,
    plot_line_chart,
)


def plot_map_or_chart(df, granularity, plot_type, variable):
    # Remove -999 values before aggregation
    df = df[df["rain"] != -999]
    df = df[df["tmin"] != -999]
    df = df[df["tmax"] != -999]

    if granularity == "state":
        df = (
            df.groupby("state", as_index=False)
            .agg({"rain": "mean", "tmin": "mean", "tmax": "mean"})
            .fillna(0)
        )

    if plot_type == "choropleth_mapbox":
        return plot_choropleth_map(df, granularity, variable)
    elif plot_type == "barchart":
        return plot_barchart(df, granularity)
    elif plot_type == "scatter":
        return plot_scatter(df, granularity)
    elif plot_type == "histogram":
        return plot_histogram(df, granularity)
    elif plot_type == "boxplot":
        return plot_boxplot(df, granularity)
    elif plot_type == "heatmap":
        return plot_heatmap(df, granularity)
    elif plot_type == "count chart":
        return plot_count_chart(df, granularity)
    elif plot_type == "line chart":
        return plot_line_chart(df, granularity)


def main():
    # Sidebar selections
    granularity = st.sidebar.selectbox("Select granularity:", ["state", "district"])
    frequency = st.sidebar.selectbox(
        "Select frequency:", ["daily", "monthly", "yearly"]
    )
    variable = st.sidebar.selectbox(
        "Select variable to plot:", ["rain", "tmin", "tmax"]
    )
    plot_type = st.sidebar.selectbox(
        "Select plot type:",
        [
            "choropleth_mapbox",
            "barchart",
            "scatter",
            "histogram",
            "boxplot",
            "heatmap",
            "count chart",
            "line chart",
        ],
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
        fig = plot_map_or_chart(data, granularity, plot_type, variable)
        st.plotly_chart(fig)
    else:
        st.write("No data found or an error occurred while querying.")


if __name__ == "__main__":
    main()
