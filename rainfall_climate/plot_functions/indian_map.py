import plotly.express as px
import plotly.graph_objects as go
import json


def plot_choropleth_map(df, granularity, variable):
    if granularity == "district":
        geojson_filepath = (
            "rainfall_climate/utilities/geoBoundaries-IND-ADM2_simplified.geojson"
        )
        featureidkey = "properties.shapeName"  # Assuming 'shapeName' matches your 'district' column
        locations = "district"
    else:
        geojson_filepath = "rainfall_climate/utilities/indian_states.geojson"
        featureidkey = "properties.ST_NM"  # Ensure 'ST_NM' matches your 'state' column
        locations = "state"

    with open(geojson_filepath) as f:
        geojson = json.load(f)

    # Ensure the DataFrame matches the GeoJSON properties
    df[locations] = df[locations].str.title()  # Ensure title case matches GeoJSON

    # Normalize the range of the selected variable to [0, 1]
    min_val = df[variable].min()
    max_val = df[variable].max()
    if min_val != max_val:
        df["normalized_var"] = (df[variable] - min_val) / (max_val - min_val)
    else:
        df["normalized_var"] = df[variable]

    # Define the color scale
    color_scale = [[0, "white"], [0.0001, "lightblue"], [1, "darkblue"]]

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations=locations,
        featureidkey=featureidkey,
        color="normalized_var",
        color_continuous_scale=color_scale,
        mapbox_style="carto-positron",
        zoom=3.4,
        center={"lat": 22.9734, "lon": 78.6569},
        opacity=0.5,
        labels={"normalized_var": f"{variable.capitalize()} (normalized)"},
        hover_data={locations: True, variable: True, "normalized_var": False},
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def plot_barchart(df, granularity):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df[granularity], y=df["rain"], name="Rainfall", marker=dict(color="blue")
        )
    )

    fig.update_layout(
        title=f"Rainfall by {granularity.capitalize()}",
        xaxis_title=granularity.capitalize(),
        yaxis_title="Rainfall (mm)",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def plot_scatter(df, granularity):
    fig = px.scatter(
        df, x=granularity, y="rain", color="rain", title="Scatter Plot of Rainfall"
    )
    return fig


def plot_histogram(df, granularity):
    fig = px.histogram(df, x="rain", title="Histogram of Rainfall")
    return fig


def plot_boxplot(df, granularity):
    fig = px.box(df, x=granularity, y="rain", title="Box Plot of Rainfall")
    return fig


def plot_heatmap(df, granularity):
    fig = px.density_heatmap(df, x=granularity, y="rain", title="Heatmap of Rainfall")
    return fig


def plot_count_chart(df, granularity):
    df_count = df.groupby(granularity).size().reset_index(name="count")
    fig = px.bar(df_count, x=granularity, y="count", title="Count Chart")
    return fig


def plot_line_chart(df, granularity):
    fig = px.line(df, x=granularity, y="rain", title="Line Chart of Rainfall")
    return fig


def plot_map_or_chart(df, granularity, variable, plot_type):
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
