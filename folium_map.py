import pandas as pd
import folium
import streamlit as st
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
    m = folium.Map(
        location=[df.iloc[0]["latitudine"], df.iloc[0]["longitudine"]], zoom_start=13
    )
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


def main():
    st.title("Folium Map in Streamlit")
    df = generate_random_record(80)
    map_ = create_map(df)
    folium_static(map_, height=500)


if __name__ == "__main__":
    main()
