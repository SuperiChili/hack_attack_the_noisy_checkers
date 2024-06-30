import streamlit as st
import pandas as pd
from datetime import time, timedelta

import folium
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional
from streamlit_folium import st_folium

from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static

container = st.container

# Example DataFrame
data = {
    'latitude': [43.7696, 43.7623, 43.7590, 43.7600, 43.7700, 43.7599, 43.7500, 43.7640, 43.7680, 43.7800],
    'longitude': [11.2558, 11.2658, 11.2458, 11.2550, 11.2650, 11.2650, 11.2690, 11.2350, 11.2450, 11.2350],
    'intensity': [100, 60, 30, 100, 60, 60, 30, 30, 100, 100]  # Varied intensities
}

# Assuming 'data' is defined and contains your data
df = pd.DataFrame(data)

def map_color(intensity):
    if intensity <= 30:
        return [0, 255, 0]
    elif intensity <= 60:
        return [255, 255, 0]
    else:
        return [255, 0, 0]
    
df['color'] = df['intensity'].apply(map_color)

# Prepare the complete configuration including map state and layers
complete_config = {
    'version': 'v1',
    'config': {
        'mapState': {
            'latitude': 43.7696,
            'longitude': 11.2558,
            'zoom': 12
        },
        'layers': [{
            'id': 'points',
            'type': 'point',
            'config': {
                'dataId': 'data',
                'label': 'Intensity Points',
                'color': [
                    {'field': 'color', 'value': ['red', 'green', 'yellow'], 'scale': 'ordinal'}
                ],
                'size': 3,  # Adjust size here
            },
            'visualChannels': {
                'latitudeField': {'name': 'latitude', 'type': 'real'},
                'longitudeField': {'name': 'longitude', 'type': 'real'},
                'colorField': {'name': 'color', 'type': 'string'},
                'sizeField': {'name': 'intensity', 'type': 'real'},
                'sizeScale': 'sqrt'
            }
        }]
    }
}

# Create a KeplerGl map with the complete configuration
map_1 = KeplerGl(height=500, width=8000)
map_1.config = complete_config

# Add data to the map
map_1.add_data(data=df, name="sound_intensity")

# If the map still doesn't center as expected, explicitly set the map state again
map_1.config['mapState'] = {
    'latitude': 43.7696,
    'longitude': 11.2558,
    'zoom': 12
}

st.selectbox("giorno", ("LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"), index=None, placeholder="Scegli un giorno", label_visibility="hidden")
st.slider("orario", label_visibility="hidden", min_value=(time(00, 00)), max_value=(time(23, 00)), value=(time(00, 00)), step=timedelta(hours=1),)
# Display the map in Streamlit
keplergl_static(map_1)

#########################
st.set_page_config(layout="wide")


@st.cache_resource
def get_data() -> List[Dict]:
    api_key = st.secrets["api_key"]
    url = f"https://developer.nps.gov/api/v1/parks?api_key={api_key}&limit=500"
    resp = requests.get(url)
    data = resp.json()["data"]
    parks = [park for park in data if park["designation"] == "National Park"]

    for park in parks:
        park["_point"] = Point.from_dict(park)

    return parks


@dataclass
class Point:
    lat: float
    lon: float

    @classmethod
    def from_dict(cls, data: Dict) -> "Point":
        if "lat" in data:
            return cls(float(data["lat"]), float(data["lng"]))
        elif "latitude" in data:
            return cls(float(data["latitude"]), float(data["longitude"]))
        else:
            raise NotImplementedError(data.keys())

    def is_close_to(self, other: "Point") -> bool:
        close_lat = self.lat - 0.0001 <= other.lat <= self.lat + 0.0001
        close_lon = self.lon - 0.0001 <= other.lon <= self.lon + 0.0001
        return close_lat and close_lon


@dataclass
class Bounds:
    south_west: Point
    north_east: Point

    def contains_point(self, point: Point) -> bool:
        in_lon = self.south_west.lon <= point.lon <= self.north_east.lon
        in_lat = self.south_west.lat <= point.lat <= self.north_east.lat

        return in_lon and in_lat

    @classmethod
    def from_dict(cls, data: Dict) -> "Bounds":
        return cls(
            Point.from_dict(data["_southWest"]), Point.from_dict(data["_northEast"])
        )


#############################
# Streamlit app
#############################

"## National Parks in the United States"

"""
The National Parks Service provides an
[API](https://www.nps.gov/subjects/digital/nps-data-api.htm) to programmatically explore
NPS data.

We can take data about each park and display it on the map _conditionally_ based on
whether it is in the viewport.

---
"""

# define layout
c1, c2 = st.columns(2)

# get and cache data from API
parks = get_data()

# layout map
with c1:
    """(_Click on a pin to bring up more information_)"""
    m = folium.Map(location=[39.949610, -75.150282], zoom_start=4)

    for park in parks:
        popup = folium.Popup(
            f"""
                  <a href="{park["url"]}" target="_blank">{park["fullName"]}</a><br>
                  <br>
                  {park["operatingHours"][0]["description"]}<br>
                  <br>
                  Phone: {park["contacts"]["phoneNumbers"][0]["phoneNumber"]}<br>
                  """,
            max_width=250,
        )
        folium.Marker([park["latitude"], park["longitude"]], popup=popup).add_to(m)

    map_data = st_folium(m, key="fig1", width=700, height=700)

# get data from map for further processing
map_bounds = Bounds.from_dict(map_data["bounds"])

# when a point is clicked, display additional information about the park
try:
    point_clicked: Optional[Point] = Point.from_dict(map_data["last_object_clicked"])

    if point_clicked is not None:
        with st.spinner(text="loading image..."):
            for park in parks:
                if park["_point"].is_close_to(point_clicked):
                    with c2:
                        f"""### _{park["fullName"]}_"""
                        park["description"]
                        st.image(
                            park["images"][0]["url"],
                            caption=park["images"][0]["caption"],
                        )
                        st.expander("Show park full details").write(park)
except TypeError:
    point_clicked = None

# even though there is a c1 reference above, we can do it again
# output will get appended after original content
with c1:
    parks_in_view: List[Dict] = []
    for park in parks:
        if map_bounds.contains_point(park["_point"]):
            parks_in_view.append(park)

    "Parks visible:", len(parks_in_view)
    "Bounding box:", map_bounds