import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium

# Function to parse SQL file and return a DataFrame
def parse_sql_to_df(file_path):
    data = []  # List to hold parsed data
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('insert into MOCK_DATA'):
                # Extracting values between parentheses
                values_str = line.split('values')[-1].strip().strip('();')
                values = values_str.split(', ')
                # Appending a dictionary for each row of data
                data.append({
                    'id': int(values[0]),
                    'rest': values[1].strip("'"),
                    'latitudine': float(values[2]),
                    'longitudine': float(values[3]),
                    'noise': int(values[4])
                })
    return pd.DataFrame(data)

# Function to determine marker color based on noise level
def get_color(noise):
    if noise <= 30:
        return 'green'
    elif noise <= 60:
        return 'yellow'
    else:
        return 'red'

# Function to create a map and add markers based on the DataFrame
def create_map(df):
    # Initialize map centered around the first restaurant
    m = folium.Map(location=[df.iloc[0]['latitudine'], df.iloc[0]['longitudine']], zoom_start=14)
    # Add markers
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitudine'], row['longitudine']],
            popup=f"{row['rest']}: Noise {row['noise']}",
            icon=folium.Icon(color=get_color(row['noise']))
        ).add_to(m)
    return m

# Main function to run the script
def main():
    st.title("Folium Map in Streamlit")
    df = parse_sql_to_df('4_rest.sql')  # Adjust the file path as necessary
    map_ = create_map(df)
    # Display the map using st_folium
    st_folium(map_, height=500)

if __name__ == "__main__":
    main()