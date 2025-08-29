from datetime import datetime
import streamlit as st
import requests
import pandas as pd

'''
# TaxiFareModel
'''

# add some controllers to ask the user to select the parameters of the ride

# 1. Let's ask for:
# - date and time
# - pickup longitude
# - pickup latitude
# - dropoff longitude
# - dropoff latitude
# - passenger count

# Date and time input
st.subheader("📅 Trip Details")
col1, col2 = st.columns(2)

with col1:
    pickup_date = st.date_input(
        "Pickup Date",
        value=datetime.now().date()
    )

with col2:
    pickup_time = st.time_input(
        "Pickup Time",
        value=datetime.now().time()
    )

# Combine date and time
pickup_datetime = datetime.combine(pickup_date, pickup_time)

# Location inputs
st.subheader("📍 Pickup Location")
col1, col2 = st.columns(2)

with col1:
    pickup_longitude = st.number_input(
        "Pickup Longitude",
        value=-73.985664,
        format="%.6f",
        help="NYC longitude range: approximately -74.25 to -73.70"
    )

with col2:
    pickup_latitude = st.number_input(
        "Pickup Latitude",
        value=40.748441,
        format="%.6f",
        help="NYC latitude range: approximately 40.49 to 40.91"
    )

st.subheader("🎯 Dropoff Location")
col1, col2 = st.columns(2)

with col1:
    dropoff_longitude = st.number_input(
        "Dropoff Longitude",
        value=-73.985664,
        format="%.6f",
        help="NYC longitude range: approximately -74.25 to -73.70"
    )

with col2:
    dropoff_latitude = st.number_input(
        "Dropoff Latitude",
        value=40.748441,
        format="%.6f",
        help="NYC latitude range: approximately 40.49 to 40.91"
    )

# Passenger count
st.subheader("👥 Passengers")
passenger_count = st.selectbox(
    "Number of Passengers",
    options=[1, 2, 3, 4, 5, 6, 7, 8],
    index=0
)

url = 'https://taxifare-283984718972.europe-west1.run.app/predict'

st.subheader("🚖 Get Fare Prediction")

if st.button("Predict Fare", type="primary"):

    # 2. Let's build a dictionary containing the parameters for our API...

    params = {
        'pickup_datetime': pickup_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'pickup_longitude': pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude': dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
    }

    # Display the parameters being sent
    with st.expander("📋 Parameters sent to API"):
        st.json(params)

    # 3. Let's call our API using the `requests` package...


    try:
            with st.spinner('Getting prediction from API...'):
                # Make the API call
                response = requests.get(url, params=params)
                st.write(response.status_code)

            # 4. Let's retrieve the prediction from the **JSON** returned by the API...

            if response.status_code == 200:
                prediction = response.json()

                '''
                ## Finally, we can display the prediction to the user
                '''

                # Display the prediction
                st.success("✅ Prediction received!")

                # Extract fare from response (adjust key name based on your API response format)
                if 'fare' in prediction:
                    fare = prediction['fare']
                elif 'prediction' in prediction:
                    fare = prediction['prediction']
                else:
                    # If unsure about the response structure, display the whole response
                    st.json(prediction)
                    fare = list(prediction.values())[0] if prediction else "Unknown"

                # Display the fare in a nice format
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.metric(
                        label="💰 Predicted Taxi Fare",
                        value=f"${fare:.2f}" if isinstance(fare, (int, float)) else str(fare)
                    )

                # Show trip summary
                st.subheader("📊 Trip Summary")
                trip_data = {
                    'Parameter': ['Date & Time', 'Pickup Location', 'Dropoff Location', 'Passengers'],
                    'Value': [
                        pickup_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        f"({pickup_latitude:.4f}, {pickup_longitude:.4f})",
                        f"({dropoff_latitude:.4f}, {dropoff_longitude:.4f})",
                        passenger_count
                    ]
                }

                df = pd.DataFrame(trip_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.write("Response:", response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection Error: {str(e)}")
        st.info("💡 Make sure the API URL is correct and the service is running.")
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")

# Add some helpful information
st.markdown("---")
st.markdown("### 💡 Tips")
st.markdown("""
- **Default coordinates** are set to NYC area (around Times Square)
- **Longitude** values in NYC are typically between -74.25 and -73.70
- **Latitude** values in NYC are typically between 40.49 and 40.91
- The prediction model expects parameters in the format shown above
""")

# Optional: Add a map for better UX
st.markdown("### 🗺️ Location Visualization")
if st.checkbox("Show pickup and dropoff on map"):
    map_data = pd.DataFrame({
        'lat': [pickup_latitude, dropoff_latitude],
        'lon': [pickup_longitude, dropoff_longitude],
        'type': ['🚖 Pickup', '🎯 Dropoff']
    })
    st.map(map_data)
