'''
Class: CS230 -- 3
Name: Jared Podrazik
Description: The Global Volcano Explorer is an interactive web app built with Streamlit that lets users explore
volcano data from the Smithsonian. Users can filter volcanoes by region, elevation, eruption year, and type
using sliders, dropdowns, and checkboxes. The app includes maps, bar charts, and histograms to visualize
patterns and trends, and highlights volcanoes with notable features like “Mount” in their names. It combines
Python, Pandas, Matplotlib, and PyDeck for a clean and engaging data experience.
'''

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator                                               # Customizes plot axis

# [ST4] Sets up the app page configuration
st.set_page_config(
    page_title="Volcano Explorer",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded")

# [PY4] Dictionary for chart color customization
chart_colors = {
    "Volcano Type by Region": "skyblue",
    "Elevation by Region": "lightgreen",
    "Types in Region with Known Eruptions": "salmon"}

# [PY1] Function to count volcanoes and calculate the average elevation for a given region
# [PY2] Function that returns both count and average calculation
def count_and_average_height(df, region="All"):
    if region != "All":                                                                 # If a specific region is selected, filter the data
        df = df[df["volcanic region"] == region]
    return len(df), df["elevation (m)"].mean()                                          # Return the count and average

@st.cache_data  # Cache the data
# [DA1] Function to load and clean data
# [DA9] Add a new column or perform calculations on DataFrame columns
def load_data():
    df = pd.read_excel("volcanoes.xlsx")
    df.columns = df.columns.str.strip().str.lower()                                     # Clean the column names by removing any spaces and making them lowercase
    df["last known eruption"] = df["last known eruption"].replace(["Unknown", "?", "No data", ""], pd.NA)       # Handle missing values in eruption data
    df["year erupted"] = pd.to_numeric(df["last known eruption"].str.extract(r'(\d{4})')[0], errors='coerce')   # Extract the year from the eruption data
    return df


# [PY3] List comprehension to get volcano names that contain "Mount" in them
def get_named_volcanoes(df):
    return [name for name in df["volcano name"] if "Mount" in name]                     # Return volcano names that contain 'Mount'


# Home Page
def home(df):
    st.title("🌋 Welcome to the Global Volcano Explorer")                               # Display the title of the webpage
    st.subheader("Analyze, visualize, and explore data on over 1,500 volcanoes around the world using various charts and maps.")  # Display the subtitle

    st.markdown("**Some Volcano Fun Facts:**")
    st.markdown("1. The Ring of Fire, which is located in the Pacific ocean, is home to about 75% of Earth's volcanoes.")  # Add Fun facts into the home page
    st.image("Ring_of_Fire.jpg", use_container_width=True)                              # Display the Ring of Fire image

    st.markdown("\n\n"
                "2. A simple large eruption can release more energy than hundreds of atomic bombs!\n\n"
                "3. The color of lava is not always red, it can even be blue, green, or black depending on the temperature and chemicals in it.\n\n")  # More Fun facts
    st.image("Lava_color.jpeg", use_container_width=True)                               # Display the Lava color image under the second fact

    st.markdown("Use the sidebar on the left to start exploring the volcano dataset!")

    # [VIZ1] Map of all the volcanoes
    if st.checkbox("Show volcano map preview"):
        st.subheader("🌍 Global Volcano Locations")

        st.pydeck_chart(pdk.Deck(                                                       # Creates a map using Pydeck to display the volcano locations
            map_style="mapbox://styles/mapbox/light-v9",                                # Changes the Map style to light
            layers=[                                                                    # Helps to add layers for the volcanoes, which gives better visualizations
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[longitude, latitude]',                               # Get latitude and longitude for the volcano locations
                    get_radius=50000,                                                   # Set the radius for each point on the map
                    get_fill_color='[200, 30, 0, 160]',                                 # Set the color of the points to red
                    pickable=True,                                                      # Allows the user to hover over the points and get information
                )
            ],
            tooltip={                                                                   # Shows the volcano details when hovering over points
                "text": "{volcano name}\nCountry: {country}\nElevation: {elevation (m)} m"
            }
        ))


# Query 1
def query1(df):
    st.header("1. Most Common Volcano Type by Region")
    region_options = ["-- Please select a region --"] + sorted(df["volcanic region"].dropna().unique())  # Get all the unique regions and sort them
    region = st.selectbox("Select a Region or Continent:", region_options)              # Lets the user pick a region

    filtered = df if region == "-- Please select a region --" else df[df["volcanic region"] == region]  # Filters the data based on the selected region
    type_counts = filtered["primary volcano type"].value_counts()                       # Counts the volcano types in the selected region

    # [VIZ2] - Bar Chart
    st.bar_chart(type_counts)

    # Shows the volcanoes with "Mount" in their names for the selected region
    named_volcanoes = get_named_volcanoes(filtered)

    # Display the list of volcanoes with better formatting
    st.markdown(f"##### Named Volcanoes Containing 'Mount' in {region}:")               # Displays the sub-header
    if named_volcanoes:
        st.markdown("Here are the volcanoes with 'Mount' in their name:")
        for volcano in named_volcanoes:
            st.markdown(f"- **{volcano}**")                                             # Displays each volcano name as a bullet point
    else:
        st.markdown("No volcanoes with 'Mount' in their name found in this region.")


# Query 2
def query2(df):
    st.header("2. Volcanoes Over a Certain Elevation in a Region")
    region_options = ["-- Please select a region --"] + sorted(df["volcanic region"].dropna().unique())  # Get all unique regions and sort them
    region = st.selectbox("Select a Region:", region_options)                           # Lets the user select a region
    height = st.slider("Minimum Elevation (meters):", 0, 9000, 2000, 100)               # Lets the user choose the minimum elevation

    # If no region is selected, filter only by elevation, otherwise filter by both region and elevation
    if region == "-- Please select a region --":
        filtered = df[df["elevation (m)"] >= height]                                    # Filter by elevation only
    else:
        filtered = df[
            (df["volcanic region"] == region) & (df["elevation (m)"] >= height)]        # Filter by both region and elevation

    count, avg_height = count_and_average_height(filtered, region)
    st.dataframe(filtered[["volcano name", "country", "elevation (m)"]])                # Display the filtered data in a Table
    st.markdown(f"**There are {count} volcanoes above {height} in {region} with an average elevation of {avg_height:.2f} meters.**")

    # [VIZ3] Displays a Bar Chart
    fig, ax = plt.subplots()
    ax.hist(filtered["elevation (m)"], bins=20, color=chart_colors["Elevation by Region"], edgecolor="black")  # Create a histogram of elevations
    ax.set_title("Distribution of Volcano Elevations")
    ax.set_xlabel("Elevation (m)")
    ax.set_ylabel("Frequency")
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)                                  # Adds grid lines to the chart
    st.pyplot(fig)


# Query 3
def query3(df):
    st.header("3. Volcanoes Erupted Between Years in Tectonic Setting")
    min_year = int(df["year erupted"].dropna().min()) if not df["year erupted"].dropna().empty else 0       # Get the earliest eruption year from the dataset
    years = st.slider("Select Eruption Year Range:", min_year, 2025, (min_year, 2025))  # Select the year
    setting_options = ["-- Please select a tectonic setting --"] + sorted(df["tectonic setting"].dropna().unique())  # Get tectonic settings for the volcanoes
    setting = st.selectbox("Select a Tectonic Setting:", setting_options)               # Let the user select a tectonic setting

    # Filter the data based on the selected year range and tectonic setting
    filtered = df[df["year erupted"].between(years[0], years[1])] if setting == "-- Please select a tectonic setting --" else \
        df[(df["year erupted"].between(years[0], years[1])) & (df["tectonic setting"] == setting)]

    st.dataframe(filtered[["volcano name", "country", "year erupted", "tectonic setting"]]) # Display a table of the filtered volcanoes
    st.markdown(f"**There have been {len(filtered)} eruptions between {years[0]} and {years[1]}.**")

    # [VIZ4] - Display the map for the filtered volcanoes
    if filtered[["latitude", "longitude"]].dropna().empty:                              # If there are no values
        st.warning("No valid coordinates available to display on the map.")
    else:
        st.pydeck_chart(pdk.Deck(
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered,
                    get_position='[longitude, latitude]',
                    get_radius=3,
                    radius_units="pixels",
                    get_fill_color='[0, 0, 255, 160]',
                    pickable=True
                )
            ],
            tooltip={
                "text": "{volcano name}\nYear: {year erupted}\nCountry: {country}"      # Tooltip for the user
            }
        ))

# Query 4
def query4(df):
    st.header("4. Most Common Volcano Types in Selected Region with Known Eruptions")
    types = st.multiselect("Select Volcano Type(s):", sorted(df["primary volcano type"].dropna().unique()))  # Let the user select volcano types
    region_options = ["-- Please select a region --"] + sorted(df["volcanic region"].dropna().unique())      # Filter to find all the regions
    region = st.selectbox("Select a Region or Continent:", region_options)              # Let the user select a region
    known_only = st.checkbox("Only Include Volcanoes with Known Eruption Dates?", value=False)  # Checkbox to filter volcanoes with known eruptions

    filtered = df.copy()
    if known_only:
        filtered = filtered[filtered["last known eruption"].notna()]                    # If the checkbox is clicked, filter by known eruptions
    if region != "-- Please select a region --":
        filtered = filtered[filtered["volcanic region"] == region]                      # Is the bar is not empty, filter by region
    if types:
        filtered = filtered[filtered["primary volcano type"].isin(types)]               # If type is chosen, filter by selected volcano types

    type_counts = filtered["primary volcano type"].value_counts()                       # Count the number of volcano types

    # [VIZ5] Display the data in a bar chart
    fig, ax = plt.subplots(figsize=(12, 6))                                             # Create a bar chart to show the top volcano values
    top_types = type_counts.head(10)
    bars = ax.bar(top_types.index, top_types.values, color=chart_colors["Types in Region with Known Eruptions"])
    ax.set_title("Top Volcano Types in Selected Region")
    ax.set_xlabel("Volcano Type")
    ax.set_ylabel("Count")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))                               # Make sure the y-axis is integer-based
    ax.tick_params(axis='x', rotation=0 if len(top_types) <= 5 else 45)                 # Rotate x-axis labels if it's too crowded and necessary
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)                                  # Add grid lines for easier visualization

    for bar in bars:
        height = bar.get_height()                                                       # Find the height of the bars
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),                     # Tells the program where to display the number
        xytext = (0, 5), textcoords = "offset points", ha = 'center', va = 'bottom')    # Correctly puts it above the bar in the middle

    st.pyplot(fig)


# Main App
def main():
    df = load_data()                                                                    # Load the volcano data

    st.sidebar.title("🔍 Volcano Explorer Navigation")                                  # Sidebar title
    st.sidebar.markdown("Volcano Explorer")
    st.sidebar.markdown("""
    Click the dropdown to explore a dataset of volcanoes from around the world.  
    """)

    page = st.sidebar.selectbox(
        "Choose a query:",
        (
            "Home",
            "Volcano Type by Region",
            "Elevation by Region",
            "Eruptions by Year",
            "Types in Region with Known Eruptions"
        )
    )

    if page == "Home":
        home(df)
    elif page == "Volcano Type by Region":
        query1(df)
    elif page == "Elevation by Region":
        query2(df)
    elif page == "Eruptions by Year":
        query3(df)
    elif page == "Types in Region with Known Eruptions":
        query4(df)

# Run the app
if __name__ == "__main__":
    main()