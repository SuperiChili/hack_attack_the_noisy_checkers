import pandas as pd
import folium
import geocoder
import streamlit as st
from datetime import time, timedelta, datetime as dt
from streamlit_folium import st_folium, folium_static
import random


def get_color(noise):
    if noise <= 30:
        return "green"
    elif noise <= 60:
        return "orange"
    else:
        return "red"

def get_current_gps_coordinates():
    g = geocoder.ip('me')
    if g.latlng is not None:
        st.write(g.latlng)
        return g.latlng
    else:
        return None
#per motivi ignoti, l'ip della scuola e' in mezzo ai binari, le vere coordinate della scuola sono a seguire
#43.77105336151461, 11.242748838610913

def create_map(df):
    my_position = get_current_gps_coordinates()
    latitude, longitude = my_position
    m = folium.Map(location=[latitude, longitude], zoom_start=13)
    folium.Marker(
            location=[latitude, longitude],
            popup=f"mia posizione",
            icon=folium.Icon(color="black", icon="arrow-down")
        ).add_to(m)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["latitudine"], row["longitudine"]],
            popup=f"{row['rest']}: Noise {row['noise']}",
            icon=folium.Icon(color=get_color(row["noise"])),
        ).add_to(m)
    return m

def generate_random_record(qnt=10):
    data = []
    for i in range(1, qnt + 1):
        data.append(
            {
                "id": i,
                "rest": f"Restaurant {i}",
                "latitudine": random.uniform(43.7600, 43.7900),
                "longitudine": random.uniform(11.2300, 11.2800),
                "noise": random.randint(20, 100),
            }
        )
    return pd.DataFrame(data)


now = dt.now()

@st.cache_data
def take_time():
    current_time = now.time()
    return (current_time)

def main():
    st.title("Rumorosità dei ristoranti a Firenze")
   
    current_weekday = now.weekday()
    selected_day = st.selectbox("giorno",
                  ("Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"),
                    index=current_weekday, 
                    placeholder="Scegli un giorno", 
                    label_visibility="hidden")

    selected_hour = st.slider("orario", 
              label_visibility="hidden", 
              min_value=(time(00, 00)), 
              max_value=(time(23, 00)), 
              value=(take_time()), 
              step=timedelta(hours=1))
    df = generate_random_record(20)
    st.write(df)
    map_ = create_map(df)
    folium_static(map_, height=500)


if __name__ == "__main__":
    main()
