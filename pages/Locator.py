from geopy.geocoders import Nominatim
import json
import time
import streamlit as st

OFP = "C:\\Users\\Owner\\Desktop\\map\\"


def get_lat_long(city_name):
    time.sleep(1)
    geolocator = Nominatim(user_agent="geo-locator")
    location = geolocator.geocode(city_name, exactly_one=True, language="en")
    
    country = location._address.split(",")[-1]
    city_name = location._address.split(",")[0]

    if location:
        return CITY(city_name, country, location.latitude, location.longitude)
    else:
        return None

class CITY:
    def __init__(self, name, country, LAT, LON):
        self.name = name
        self.country = country
        self.LAT = LAT
        self.LON = LON

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "LAT": self.LAT,
            "LON": self.LON  # Added 'self.'
        }


#==============
st.set_page_config(page_title="City locator", page_icon="🗺️")
st.title("City locator")
st.write("Enter the city names you want to travel to.")
st.write("Once ready, press the 'Find cities' button. This will find the location of the cities, so they can be plotted on a world map.")
st.write("Spelling matters, and if a city is spelt correctly but cannot be found, enter the country name also. For example Bangkok, Thailand.")
st.write("If you have a long list of cities, to avoid repeating this step it is advised to download the JSON data - which can then be uploaded to the Map page.")
st.write("----------------")

if 'ilist' not in st.session_state:
    st.session_state.ilist = []

# Input to add new item
new_item = st.text_input("Add an item:")

if st.button("Add"):
    if new_item:
        st.session_state.ilist.append(new_item)
        st.rerun()

# Display the list with remove buttons
st.write("### List of Items")
for i, item in enumerate(st.session_state.ilist):
    col1, col2 = st.columns([0.8, 0.2])
    col1.write(item)
    if col2.button("Remove", key=i):
        st.session_state.ilist.pop(i)
        st.rerun()

#===============

CITIES = ["London", 
          "Bangkok", 
          "Krabi, Thailand", 
          "Phuket, Thailand", 
          "Singapore", 
          "Beijing, China", 
          "Xi An, China", 
          "Zhangjiajie, China",
          "Chongqing, China",
          "Shanghai",
          "Tokyo",
          "Fujiyoshida",
          "Osaka",
          "Kyoto",
          "Hanoi",
          "Sapa, Vietnam",
          "Ho Chi Minh, Vietnam",
          "Da Nang, Vietnam",
          "New Delhi",
          "Jaipur",
          "Udaipur",
          "Agra",
          "Jodhpur",
          "Mumbai",
          ]

CBOX = st.checkbox("Debugging mode, MJ cities")
if CBOX:
    st.session_state.ilist = []
    for c in CITIES:
        st.session_state.ilist.append(c)

if len(st.session_state.ilist)>0:

    if st.button("Find cities!"):
        cObjs = []
        for city in st.session_state.ilist:
            st.write("Getting LAT/LON of: " +str(city))
            cObjs.append(get_lat_long(city))

        
        output_data = json.dumps([city.to_dict() for city in cObjs], indent=4)
        st.session_state.output_data = output_data

        st.write(output_data)

        st.download_button(
            label="Download JSON",
            data=output_data,
            file_name="output.txt",
            mime="application/json"
        )
