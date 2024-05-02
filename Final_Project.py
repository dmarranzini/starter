"""
 Class: CS230--Section 03 
Name: Diego Marranzini
 Description: (Give a brief description for Exercise name--See 
below)
 I pledge that I have completed the programming assignment 
independently. 
I have not copied the code from a student or any source.
 I have not given my code to any student. 
"""

import streamlit as st  # [ST4] Using Streamlit for app development
import pandas as pd  # Utilizing pandas for data manipulation
import matplotlib.pyplot as plt  # [VIZ2] Using matplotlib for plotting graphs
import seaborn as sns  # [VIZ3] Using seaborn for enhanced visual effects on plots
import folium  # [VIZ1] Using folium for detailed maps
from folium.plugins import MarkerCluster
from folium.vector_layers import PolyLine
from streamlit_folium import folium_static
import numpy as np  # Using numpy for numerical operations
import os  # For operating system dependent functionality

st.markdown(
    """
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .streamlit-expander {
        margin: 5px 0px;  # Adds space around expanders
    }
    </style>
    """, unsafe_allow_html=True)  # [ST4] Custom styles applied to Streamlit components


# [PY1] Function to convert kilotons to megatons with default parameter value
def kt_to_mt(value):
    return value / 1000.0


# [PY2] Function that returns more than one value
def calculate_blast_radii(yield_mt):
    fireball_radius = np.sqrt(yield_mt) * 0.6  # approximate fireball radius in miles
    airblast_radius = fireball_radius * 2  # air blast radius in miles
    thermal_radiation_radius = fireball_radius * 3  # thermal radiation radius in miles
    return fireball_radius, airblast_radius, thermal_radiation_radius


# [PY3] Function that returns a value and is called in multiple places
def calculate_stats(column):
    if column.empty:
        return None, None, None
    max_val = column.max()  # [DA3] Retrieve the maximum value from the column
    min_val = column.min()  # [DA3] Retrieve the minimum value
    avg_val = column.mean()  # [DA3] Calculate the average value
    return max_val, min_val, avg_val


def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        st.success("Welcome to the Nuclear Data Analysis App!")
        data['Data.Yield.Upper'] = kt_to_mt(data['Data.Yield.Upper'])  # [PY1] Use of function with default value
        data['Data.Yield.Lower'] = kt_to_mt(data['Data.Yield.Lower'])
        return data
    except FileNotFoundError:
        st.error("File not found. Please make sure the file path is correct.")
        return pd.DataFrame()


data = load_data('nuclear_explosions.csv')

# Sidebar controls for app navigation and features
st.sidebar.title("Control Panel")  # [ST4] Sidebar used for control panel
if st.sidebar.button("Home", key="home"):  # [ST1] Button widget in sidebar
    st.experimental_rerun()

st.sidebar.header("Nuclear Explosion Simulator")  # [ST4] Header for a section in sidebar
sim_yield_mt = st.sidebar.number_input("Enter yield in Megatons:", min_value=1, max_value=100, value=1, step=1,
                                       format="%i")  # [ST1] Number input widget for simulation control
if st.sidebar.button("Simulate Explosion"):  # [ST1] Button for triggering explosion simulation
    fireball_radius, airblast_radius, thermal_radiation_radius = calculate_blast_radii(sim_yield_mt)  # [PY2]
    st.sidebar.write(f"Fireball radius: {fireball_radius:.2f} miles")
    st.sidebar.write(f"Airblast radius: {airblast_radius:.2f} miles")
    st.sidebar.write(f"Thermal radiation radius: {thermal_radiation_radius:.2f} miles")

    # Visualization of explosion effects using folium map
    map_center = [18.483402, -69.929611]
    sim_map = folium.Map(location=map_center, zoom_start=10)  # [VIZ1]
    folium.Circle(location=map_center, radius=fireball_radius * 1609.34, color='red', fill=True, fill_color='red',
                  fill_opacity=0.5, popup="Fireball Radius").add_to(sim_map)
    folium.Circle(location=map_center, radius=airblast_radius * 1609.34, color='orange', fill=True, fill_color='orange',
                  fill_opacity=0.5, popup="Airblast Radius").add_to(sim_map)
    folium.Circle(location=map_center, radius=thermal_radiation_radius * 1609.34, color='yellow', fill=True,
                  fill_color='yellow', fill_opacity=0.5, popup="Thermal Radiation Radius").add_to(sim_map)
    folium_static(sim_map)  # [ST3] Displaying the map in Streamlit

st.sidebar.header("Analyze Nuclear Explosions by Country")  # [ST4] Additional sidebar header for navigation

# Country selection and data filtering logic
if not data.empty:
    data['Date.Year'] = pd.to_numeric(data['Date.Year'], errors='coerce')  # [DA1] Data cleaning
    countries = [''] + list(data['WEAPON_SOURCE_COUNTRY'].unique())  # [PY4] Generating a list with comprehension
    selected_country = st.sidebar.selectbox("Select Country", countries)  # [ST1] Dropdown for country selection

    # Conditional display based on country selection
    if selected_country == "":
        if os.path.exists('R.png'):
            st.image('R.png', caption='Nuclear Test Visualization')
        else:
            st.error("Image not found. Make sure 'R.png' is in the correct path.")
    elif selected_country:
        min_year, max_year = int(data['Date.Year'].min()), int(data['Date.Year'].max())  # [DA2] Sorting data
        year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))  # [ST1]
        types = list(data['Data.Type'].unique())  # [PY4] List comprehension used implicitly
        type_test = st.sidebar.multiselect("Select Test Type", types, default=[])  # [ST1]

        load_button = st.sidebar.button("Load Data", help="Click here to load the data based on the selections.")
        # [ST1]

        if load_button:
            # Filtering data based on user selections
            country_data = data[data['WEAPON_SOURCE_COUNTRY'] == selected_country]  # [DA4]
            filtered_data = country_data[(country_data['Date.Year'].between(*year_range)) & (country_data['Data.Type']
                                                                                             .isin(type_test)
                                                                                             if type_test else True)]
            # [DA5]

            # Tabs
            tabs = ["Yield Over Time", "Test Depths", "Map and Stats"]
            if selected_country == "USA":
                tabs.append("Historical Bombs")
            tab_objects = st.tabs(tabs)

            with tab_objects[0]:
                st.header("Yield of Nuclear Explosions Over Time")
                fig, ax = plt.subplots()
                sns.lineplot(x='Date.Year', y='Data.Yield.Lower', data=filtered_data, ax=ax, label='Min Yield')
                # [VIZ2]
                sns.lineplot(x='Date.Year', y='Data.Yield.Upper', data=filtered_data, ax=ax, label='Max Yield')
                # [VIZ3]
                ax.set_ylabel('Yield (Megatons)')
                ax.set_title('Yield of Nuclear Explosions Over Time')
                ax.legend()
                st.pyplot(fig)

            with tab_objects[1]:
                st.header("Distribution of Nuclear Test Depths by Location")
                fig, ax = plt.subplots(figsize=(14, 10))
                sns.boxplot(y='WEAPON_DEPLOYMENT_LOCATION', x='Location.Coordinates.Depth', data=filtered_data,
                            orient='h')  # [VIZ2]
                plt.title('Distribution of Test Depths by Location', fontsize=16)
                plt.ylabel('Location', fontsize=14)
                plt.xlabel('Depth (meters)', fontsize=14)
                plt.grid(True)
                plt.yticks(fontsize=12)
                st.pyplot(fig)

            with tab_objects[2]:
                st.header("Map of Nuclear Explosion Sites and Summary Statistics")
                map = folium.Map(location=[0, 0], zoom_start=2)  # [VIZ1]
                marker_cluster = MarkerCluster().add_to(map)
                for _, row in filtered_data.iterrows():  # [DA8]
                    folium.Marker(
                        location=[row['Location.Coordinates.Latitude'], row['Location.Coordinates.Longitude']],
                        popup=f"Yield: {row['Data.Yield.Upper']} MT, Year: {row['Date.Year']}",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(marker_cluster)
                folium_static(map)

                max_yield, min_yield, avg_yield = calculate_stats(filtered_data['Data.Yield.Upper'])  # [DA9]
                if max_yield is not None:
                    st.write(f"**Maximum Yield:** {max_yield} MT")
                    st.write(f"**Minimum Yield:** {min_yield} MT")
                    st.write(f"**Average Yield:** {avg_yield} MT")
                else:
                    st.write("No data to display for selected filters.")

            if selected_country == "USA" and len(tab_objects) > 3:
                with tab_objects[3]:
                    st.header("Historical Bomb Routes: Hiroshima and Nagasaki")
                    historical_map = folium.Map(location=[33.0, 135.0], zoom_start=5)  # [VIZ1]
                    enola_gay_path = [[15.0036, 145.6355], [34.3853, 132.4553]]
                    PolyLine(enola_gay_path, color="green", weight=5, tooltip="Enola Gay to Hiroshima").add_to(
                        historical_map)
                    folium.Marker([15.0036, 145.6355], popup="Start: Tinian Island",
                                  icon=folium.Icon(color="green")).add_to(historical_map)
                    folium.Marker([34.3853, 132.4553], popup="Hiroshima: Little Boy, 15 kilotons, 1945",
                                  icon=folium.Icon(color="red")).add_to(historical_map)

                    bockscar_path = [[15.0036, 145.6355], [32.7503, 129.8777]]
                    PolyLine(bockscar_path, color="blue", weight=5, tooltip="Bockscar to Nagasaki").add_to(
                        historical_map)
                    folium.Marker([15.0036, 145.6355], popup="Start: Tinian Island",
                                  icon=folium.Icon(color="blue")).add_to(historical_map)
                    folium.Marker([32.7503, 129.8777], popup="Nagasaki: Fat Man, 21 kilotons, 1945",
                                  icon=folium.Icon(color="darkred")).add_to(historical_map)

                    folium_static(historical_map)

    else:
        st.sidebar.error("Please select a country to load data.")
else:
    st.sidebar.write("Data is not available or could not be loaded.")
