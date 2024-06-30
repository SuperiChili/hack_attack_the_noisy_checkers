import pandas as pd
import folium
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


def create_map(df):
    florence_center = [43.7696, 11.2558]
    m = folium.Map(location=florence_center, zoom_start=13)
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
    st.title("Ristoranti nella tua zona")

    current_weekday = now.weekday()
    st.selectbox("giorno",
                  ("LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"),
                    index=current_weekday, 
                    placeholder="Scegli un giorno", 
                    label_visibility="hidden")
    st.slider("orario", 
              label_visibility="hidden", 
              min_value=(time(00, 00)), 
              max_value=(time(23, 00)), 
              value=(take_time()), 
              step=timedelta(hours=1))
    df = generate_random_record(80)
    map_ = create_map(df)
    folium_static(map_, height=500)


if __name__ == "__main__":
    main()
