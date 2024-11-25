#pages/dashboard.py

import streamlit as st  # type: ignore
import requests
import psycopg2
from streamlit_extras.switch_page_button import switch_page # type: ignore

# --- PAGE CONFIG ---
st.set_page_config(page_title="SweetSpot - Dashboard", page_icon="🍰", layout="wide")

# --- SESSION CHECK ---
if 'user_info' not in st.session_state or st.session_state.user_info is None:
    st.warning("Please log in to access the dashboard.")
    st.stop()

# --- DATABASE CONNECTION ---
def get_db_connection():
    conn = psycopg2.connect(
        dbname='sweetspotdb',
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port='5432'
    )
    return conn

def get_customer_id(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sweetspot_app_customer WHERE email = %s", (email,))
    customer_id = cursor.fetchone()
    cursor.close()
    conn.close()
    return customer_id[0] if customer_id else None

# --- Function to Get Distance and Duration of an Order --- 
def get_distance(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch the order_id associated with the customer_id
    cursor.execute("SELECT id FROM sweetspot_app_order WHERE customer_id = %s", (customer_id,))
    order_id = cursor.fetchone()
    
    if order_id:
        cursor.execute("SELECT distance, duration FROM sweetspot_app_order WHERE id = %s", (order_id[0],))
        result = cursor.fetchone()
    else:
        result = None
    return result if result else (None, None)  # Return None if no result

# --- DASHBOARD PAGE ---
st.title("Dashboard")

user_first_name = st.session_state.user_info.get('first_name', 'User')
st.subheader(f"Welcome, {user_first_name}!")  # This will show first and last name

# user_last_name = st.session_state.user_info.get('last_name', '')
# st.subheader(f"Welcome, {user_first_name} {user_last_name}!")  # This will show first and last name


# --- Custom CSS Styling ---
def load_custom_css():
    st.markdown("""
    <style>
        /* Styling for cake cards */
        .cake-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
            width: 250px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            text-align: center;
            flex-shrink: 0;
        }

        /* Hover effect */
        .cake-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        /* Styling for cake image */
        .cake-image {
            border-radius: 10px;
            width: 150px;
            height: 150px;
            object-fit: cover;
            margin-bottom: 15px;
        }

        /* Styling for cake name */
        .cake-name {
            font-weight: bold;
            font-size: 1.2rem;
            color: #f76c6c;
            margin-bottom: 5px;
        }

        /* Price styling */
        .cake-price {
            font-size: 1rem;
            color: #333333;
            margin-bottom: 10px;
        }

        /* Description */
        .cake-description {
            font-size: 0.9rem;
            color: #666666;
        }
    </style>
    """, unsafe_allow_html=True)

# Load custom CSS for advanced styling
load_custom_css()


# Set the title and welcome message
st.title("Home Page")
st.write("Welcome to SweetSpot! Please use the navigation to explore our cakes, view your cart, and more.")

if st.button("View Cakes"):
    switch_page("cakes")
if st.button("Stores"):
    switch_page("stores")
if st.button("Go to Cart"):
    switch_page("cart")
if st.button("View Profile"):
    switch_page("details")
if st.button("Logout"):
    switch_page("logout")
