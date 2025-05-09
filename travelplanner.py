import streamlit as st
import os
import json
from datetime import datetime
from serpapi import GoogleSearch
from openai import OpenAI

# Load API keys securely from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

# Page setup
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.markdown("""
<style>
.title {text-align: center; font-size: 36px; font-weight: bold; color: #ff5733;}
.subtitle {text-align: center; font-size: 20px; color: #555;}
.stSlider > div {background-color: #f9f9f9; padding: 10px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# Inputs
source = st.text_input("🋦🇲 Departure City (IATA Code):", "BOM")
destination = st.text_input("🋦🇲 Destination (IATA Code):", "DEL")
departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox("🎭 Select Your Travel Theme:", ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"])
activity_preferences = st.text_area("🌍 What activities do you enjoy?", "Relaxing on the beach, exploring historical sites")

# Sidebar Preferences
st.sidebar.title("🌎 Travel Assistant")
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")

# Utilities
def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except:
        return "N/A"

def fetch_flights(source, destination, departure_date, return_date):
    try:
        params = {
            "engine": "google_flights",
            "departure_id": source,
            "arrival_id": destination,
            "outbound_date": str(departure_date),
            "return_date": str(return_date),
            "currency": "INR",
            "hl": "en",
            "api_key": SERPAPI_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("best_flights", [])[:3]
    except Exception as e:
        return []

def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful travel planning assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def research_destination():
    prompt = f"Research top attractions in {destination} for a {travel_theme.lower()} trip. Preferences: {activity_preferences}. Budget: {budget}. Hotel Rating: {hotel_rating}."
    return chat_with_gpt(prompt)

def find_hotels_and_restaurants():
    prompt = f"List top-rated hotels and restaurants in {destination} for a {travel_theme.lower()} trip. Preferences: {activity_preferences}. Budget: {budget}. Hotel Rating: {hotel_rating}."
    return chat_with_gpt(prompt)

def generate_itinerary(research, hotels, flights):
    prompt = f"Create a {num_days}-day itinerary for a {travel_theme.lower()} trip to {destination}. Activities: {activity_preferences}. Budget: {budget}. Hotel Rating: {hotel_rating}.\n\nFlights: {json.dumps(flights)}\n\nResearch: {research}\n\nHotels: {hotels}"
    return chat_with_gpt(prompt)

# Generate Plan
if st.button("🚀 Generate Travel Plan"):
    with st.spinner("✈️ Fetching flight options..."):
        flights = fetch_flights(source, destination, departure_date, return_date)

    with st.spinner("🔍 Researching destination..."):
        research = research_destination()

    with st.spinner("🏨 Finding hotels & restaurants..."):
        hotels = find_hotels_and_restaurants()

    with st.spinner("🗺️ Creating itinerary..."):
        itinerary = generate_itinerary(research, hotels, flights)

    st.subheader("✈️ Cheapest Flight Options")
    if flights:
        for flight in flights:
            st.write(f"**{flight.get('airline', 'Airline')}** - 💰 {flight.get('price', 'N/A')} - ⏱️ {flight.get('total_duration', 'N/A')}")
    else:
        st.warning("No flight data available.")

    st.subheader("🏨 Hotels & Restaurants")
    st.write(hotels)

    st.subheader("🗺️ Personalized Itinerary")
    st.write(itinerary)

    st.success("✅ Travel plan generated!")

