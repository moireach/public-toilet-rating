import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime

# Set page config
st.set_page_config(page_title="Melbourne Toilet Rater", layout="wide")

# Title
st.title("🚽 Melbourne Public Toilet Rating System")

# Introduction
st.markdown("""
Rate and review public toilets across Melbourne to help others find the best (and avoid the worst) facilities!
""")

# Load or create toilet data
@st.cache_data
def load_toilet_data():
    try:
        # Try to load existing data
        return pd.read_csv("melbourne_toilet_ratings.csv")
    except:
        # Sample data with some public toilets in Melbourne
        data = {
            "name": [
                "Flinders Street Station Toilets",
                "Queen Victoria Market Toilets",
                "Federation Square Toilets",
                "Melbourne Central Toilets",
                "State Library Toilets"
            ],
            "address": [
                "Flinders St, Melbourne VIC 3000",
                "Queen St, Melbourne VIC 3000",
                "Swanston St & Flinders St, Melbourne VIC 3000",
                "211 La Trobe St, Melbourne VIC 3000",
                "328 Swanston St, Melbourne VIC 3000"
            ],
            "latitude": [-37.8183, -37.8076, -37.8180, -37.8106, -37.8097],
            "longitude": [144.9671, 144.9580, 144.9674, 144.9628, 144.9651],
            "avg_rating": [3.5, 4.0, 4.2, 3.8, 4.1],
            "num_ratings": [12, 8, 15, 10, 7],
            "last_updated": [datetime.now().strftime("%Y-%m-%d")] * 5
        }
        return pd.DataFrame(data)

df = load_toilet_data()

# Sidebar for adding new ratings
with st.sidebar:
    st.header("Add Your Rating")
    
    # Select toilet
    selected_toilet = st.selectbox("Select a toilet", df["name"].unique())
    
    # Rating
    rating = st.slider("Rating (1-5 stars)", 1, 5, 3)
    
    # Additional feedback
    feedback = st.text_area("Additional comments (optional)")
    
    # Categories
    cleanliness = st.slider("Cleanliness", 1, 5, 3)
    amenities = st.slider("Amenities (soap, paper, etc.)", 1, 5, 3)
    accessibility = st.slider("Accessibility", 1, 5, 3)
    
    # Submit button
    if st.button("Submit Rating"):
        # Update the toilet's rating
        mask = df["name"] == selected_toilet
        current_avg = df.loc[mask, "avg_rating"].values[0]
        current_count = df.loc[mask, "num_ratings"].values[0]
        
        # Calculate new average
        new_avg = (current_avg * current_count + rating) / (current_count + 1)
        
        # Update dataframe
        df.loc[mask, "avg_rating"] = new_avg
        df.loc[mask, "num_ratings"] = current_count + 1
        df.loc[mask, "last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        # Save to CSV
        df.to_csv("melbourne_toilet_ratings.csv", index=False)
        
        st.success("Thanks for your rating! The toilet's average is now {:.1f} from {} ratings.".format(new_avg, current_count + 1))

# Main content
tab1, tab2, tab3 = st.tabs(["Map View", "Ratings Table", "Add New Toilet"])

with tab1:
    # Map view
    st.subheader("Toilet Locations")
    
    # Set the viewport location
    view_state = pdk.ViewState(
        latitude=-37.8136,
        longitude=144.9631,
        zoom=13,
        pitch=50
    )
    
    # Create a layer for the toilets
    toilet_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color="[200, 30, 0, 160]",
        get_radius=100,
        pickable=True
    )
    
    # Tooltip
    tooltip = {
        "html": "<b>{name}</b><br/>"
                "Rating: {avg_rating}/5<br/>"
                "Based on {num_ratings} ratings",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }
    
    # Render the map
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[toilet_layer],
        tooltip=tooltip
    ))

with tab2:
    # Ratings table
    st.subheader("Current Ratings")
    
    # Sort options
    sort_by = st.selectbox("Sort by", ["Highest Rated", "Most Rated", "Name"])
    if sort_by == "Highest Rated":
        display_df = df.sort_values("avg_rating", ascending=False)
    elif sort_by == "Most Rated":
        display_df = df.sort_values("num_ratings", ascending=False)
    else:
        display_df = df.sort_values("name")
    
    # Display the table with some styling
    st.dataframe(
        display_df[["name", "address", "avg_rating", "num_ratings", "last_updated"]].rename(columns={
            "name": "Name",
            "address": "Address",
            "avg_rating": "Avg Rating",
            "num_ratings": "# Ratings",
            "last_updated": "Last Updated"
        }),
        column_config={
            "Avg Rating": st.column_config.NumberColumn(
                format="%.1f ⭐",
                help="Average rating from 1-5 stars"
            )
        },
        hide_index=True,
        use_container_width=True
    )

with tab3:
    # Add new toilet form
    st.subheader("Add a New Public Toilet")
    
    with st.form("new_toilet_form"):
        name = st.text_input("Toilet Name")
        address = st.text_input("Address")
        lat = st.number_input("Latitude", value=-37.8136, format="%.6f")
        lon = st.number_input("Longitude", value=144.9631, format="%.6f")
        
        submitted = st.form_submit_button("Add Toilet")
        if submitted:
            if name and address:
                new_toilet = pd.DataFrame([{
                    "name": name,
                    "address": address,
                    "latitude": lat,
                    "longitude": lon,
                    "avg_rating": 0,
                    "num_ratings": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }])
                
                # Add to main dataframe
                df = pd.concat([df, new_toilet], ignore_index=True)
                df.to_csv("melbourne_toilet_ratings.csv", index=False)
                st.success("Toilet added successfully!")
            else:
                st.error("Please provide both a name and address")

# Footer
st.markdown("---")
st.markdown("Data is stored locally and anonymously. No personal information is collected.")