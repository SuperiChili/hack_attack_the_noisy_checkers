import pandas as pd
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static

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
        return 'yellow'
    elif intensity <= 60:
        return 'green'
    else:
        return 'intense red'
    
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
map_1 = KeplerGl(height=500, width=800)
map_1.config = complete_config

# Add data to the map
map_1.add_data(data=df, name="sound_intensity")

# If the map still doesn't center as expected, explicitly set the map state again
map_1.config['mapState'] = {
    'latitude': 43.7696,
    'longitude': 11.2558,
    'zoom': 12
}

# Display the map in Streamlit
keplergl_static(map_1)