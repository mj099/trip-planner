import streamlit as st
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from streamlit_sortables import sort_items
import json
from io import StringIO

colors = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
col_hex = ['#440154', '#481a6c', '#472f7d', '#414487', '#39568c', '#31688e', '#2a788e', '#23888e', '#1f988b', '#22a884', '#35b779', '#54c568', '#7ad151', '#a5db36', '#d2e21b']

class CITY:
    def __init__(self, name, country, LAT, LON):
        self.name = name
        self.country = country
        self.LAT = LAT
        self.LON = LON

    def __repr__(self):
        return f"CITY(name='{self.name}', LAT={self.LAT}, LON={self.LON})"

# Numbered Icon Function
def number_DivIcon(color, number):
    icon = DivIcon(
        icon_size=(150, 36),
        icon_anchor=(20, 40),
        html=f"""
            <span class='fa-stack' style='font-size: 12pt'>
                <span class='fa fa-circle-o fa-stack-2x' style='color: {color}'></span>
                <strong class='fa-stack-1x' style='color: black;'>{number:02d}</strong>
            </span>
        """
    )
    return icon

st.set_page_config(page_title="Travel planner", page_icon="👋")
st.title("City-order Planner")
st.write("First, go to the Locator page, and enter cities you want to travel to.")
st.write("Return here and organise the order of the cities into the desired travel order.")
st.write("Then click 'Plot My Route' to show the world map and the countries in order.")

if 'output_data' not in st.session_state:
    st.session_state.output_data = None
if 'ordered' not in st.session_state:
    st.session_state.ordered = None
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False
if 'folium_map' not in st.session_state:
    st.session_state.folium_map = None

f = st.file_uploader("Upload your JSON File", accept_multiple_files=False)

if f is not None:
    bytes_data = f.getvalue()
    string_io = StringIO(bytes_data.decode("utf-8"))
    data = json.load(string_io)

else:
    data = json.loads(st.session_state.output_data)

if data is not None:
    cObjs = [CITY(item["name"], item["country"], item["LAT"], item["LON"]) for item in data]
    cities = [val.name for val in cObjs]

    ordered_cities = sort_items(cities, key="sortable_list")
    st.write("### Your Destination Order:")
    st.session_state.ordered = ordered_cities
    st.write(st.session_state.ordered)

    city_to_cobj = {obj.name: obj for obj in cObjs}
    cObjs = [city_to_cobj[city] for city in ordered_cities]

    if st.button("Plot my route!"):
        st.session_state.button_clicked = True

    if st.session_state.button_clicked:
        folium_map = folium.Map(zoom_start=6, tiles="CartoDB positron")

        for i, city in enumerate(cObjs):
            color = colors[i % len(colors)]
            folium.Marker([city.LAT, city.LON], popup=city.name, icon=folium.Icon(color=color)).add_to(folium_map)
            folium.Marker(
                location=[city.LAT, city.LON],
                icon=number_DivIcon(col_hex[i % len(col_hex)], i + 1),
                z_index=1000
            ).add_to(folium_map)

        for i in range(len(cObjs) - 1):
            color = colors[i % len(colors)]
            folium.PolyLine([[cObjs[i].LAT, cObjs[i].LON], [cObjs[i + 1].LAT, cObjs[i + 1].LON]], color=color, weight=2.5, opacity=1).add_to(folium_map)

        st.session_state.folium_map = folium_map

    if st.session_state.folium_map:
        st_folium(st.session_state.folium_map, width=700, height=500)
