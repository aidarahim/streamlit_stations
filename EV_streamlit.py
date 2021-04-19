import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import folium
import json, requests
from geopy.geocoders import Nominatim
from geopy import distance
from PIL import Image

st.set_page_config(page_title='Map Out Charging Stations', page_icon=None, layout='centered', initial_sidebar_state='auto')
st.title('Supporting Clean Cars 2030')

image = Image.open('./charging_car.png')
st.image(image, caption='Electric vehicle plugged into charger')

stations = pd.read_csv('./alt_fuel_stations (Mar 23 2021).csv')

# extract stations in WA state
stations = stations[stations['State']=='WA']

# convert camelcase to snakecase
stations.columns = stations.columns.str.lower()
stations.rename(columns=lambda c: c.replace(' ','_'), inplace=True)
stations.reset_index(inplace=True,drop=False)

geolocator = Nominatim(user_agent='my_application')

# page = st.sidebar.selectbox(
#    'Select a page:',
#    ('About', 'Make a prediction')
#)

# User input

st.write('''Are you considering building a charging station at your business?''')
st.write(f'Enter your business address and we will provide information on other stations around it.')

# usr_lat = 47.617746
# usr_lng = -122.210797
# usr_lat = float(st.text_input('Please input your business latitude:', value = '47.617746'))
# usr_lng = float(st.text_input('Please input your business longitude:', value = '-122.210797'))
usr_add = st.text_input('Please input your business address:', value = '86 Pike Pl, Seattle, WA 98101')
# usr_lat = float(input("Enter the latitude: "))
# usr_lng = float(input("Enter the longitude: "))
# usr_zip = float(input("Enter the zipcode: "))

if st.button('Check now!'):

    # after initiating geocoder
    location = geolocator.geocode(usr_add)
    # returns location object with longitude, latitude and altitude instances
    usr_lat = location.latitude
    usr_lng = location.longitude

    # get zipcode from (lat,lng)
    # location = geolocator.reverse((usr_lat, usr_lng))
    # zipcode = int(location.raw['address']['postcode'])
    zipcode = int(usr_add[-5:])

    # df of all stations in that zipcode
    df_zip = stations[stations['zip']==zipcode].copy()

    df_lat = list(df_zip['latitude'])
    df_lng = list(df_zip['longitude'])

    # calculate all distance pairs
    usr_dist = []
    coords_1 = (usr_lat, usr_lng)
    for ind in range(df_zip.shape[0]):
        coords_2 = (df_lat[ind],df_lng[ind])
        usr_dist.append(distance.distance(coords_1, coords_2).miles)

    # sort distance pairs
    usr_dist = np.sort(usr_dist)

    # count number of distance pairs <0.2 miles
    count_close_by = sum(1 for i in usr_dist if i < 0.2)

    if count_close_by > 3:
        # too many charging stations close by
        st.write(f'There are more than 3 charging stations within a 0.2 mile radius.')
    else:
        # not many charging stations close by
        st.write(f'Go ahead and build a charging station!')
        st.write(f'There are less than 3 charging stations within a 0.2 mile radius.')

    # Map out business location and other charging stations
    map_wa = folium.Map(width=500, height=500,location=[usr_lat, usr_lng], zoom_start=16, control_scale=True)

    for ind in range(stations.shape[0]):
        lat = stations.loc[ind,'latitude']
        lng = stations.loc[ind,'longitude']

        folium.CircleMarker(
        [lat,lng],
        radius = 5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.5).add_to(map_wa)

    folium.CircleMarker(
    [usr_lat, usr_lng],
    radius = 10,
    color = 'green',
    fill=True,
    fill_color='green',
    fill_opacity=0.5).add_to(map_wa)

    # call to render Folium map in Streamlit
    # https://discuss.streamlit.io/t/ann-streamlit-folium-a-component-for-rendering-folium-maps/4367
    folium_static(map_wa)
