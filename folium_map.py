import pandas as pd
import folium
import json
import geocoder
import streamlit as st
from datetime import time, timedelta, datetime as dt
from streamlit_folium import st_folium, folium_static
import random


def get_color(noise):
    if noise <= 20:
        return "green"
    elif noise <= 30:
        return "orange"
    else:
        return "red"

def load_data():
    with open('restaurants.json') as f:
        restaurants = json.load(f)
    with open('noise_data.json') as f:
        noise_data = json.load(f)
    return restaurants, noise_data

def get_current_gps_coordinates():
    g = geocoder.ip('me')
    if g.latlng is not None:
        return g.latlng
    else:
        return None

def get_rest_noise(noise_data, selected_day, selected_hour, restaurant_id):
    for data in noise_data:
        if data['id'] == restaurant_id:
            noise_level = data['noise_levels'][selected_day][str(selected_hour)]
            return noise_level
    return None

def create_map(restaurants, noise_data, selected_day, selected_hour):
    my_position = get_current_gps_coordinates()
    latitude, longitude = my_position
    center_of_florence = [43.7696, 11.2558]
    m = folium.Map(location=center_of_florence, zoom_start=14)
    folium.Marker(
            location=[latitude, longitude],
            popup=f"mia posizione",
            icon=folium.Icon(color="black", icon="arrow-down")
        ).add_to(m)

    for restaurant in restaurants:
        noise=get_rest_noise(noise_data, selected_day, selected_hour, restaurant['id'])
        folium.Marker(
            location=[restaurant['latitude'], restaurant['longitude']],
            popup=f"{restaurant['name']} - {restaurant['id']}: Noise {noise}db", 
            icon = folium.Icon(color=get_color(noise))
        ).add_to(m)
    return m

def add_restaurant_markers(map_, restaurants):
    for restaurant in restaurants:
        folium.Marker(
            location=[restaurant['latitude'], restaurant['longitude']],
            popup=restaurant['name'], noise=restaurant['noise']
        ).add_to(map_)


now = dt.now()

@st.cache_data
def take_time():
    current_time = now.time()
    return (current_time)

# days = { "Lunedì": "Monday", "Martedì": "Tuesday", "Mercoledì": "Wednesday", "Giovedì": "Thursday", "Venerdì": "Friday", "Sabato": "Saturday", "Domenica": "Sunday"}
def main():
    st.title("The noisy checkers in Florence")
    current_weekday = now.weekday()
    selected_day = st.selectbox("giorno",
                  ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
                    index=current_weekday, 
                    placeholder="Scegli un giorno", 
                    label_visibility="hidden")

    selected_hour = st.slider("orario", 
              label_visibility="hidden", 
              min_value=(time(00, 00)), 
              max_value=(time(23, 00)), 
              value=(take_time()), 
              step=timedelta(hours=1))
    restaurants, noise_data = load_data()
    int_hour = selected_hour.hour
    map_ = create_map(restaurants, noise_data, selected_day, int_hour)
    folium_static(map_, height=500)

if __name__ == "__main__":
    main()
