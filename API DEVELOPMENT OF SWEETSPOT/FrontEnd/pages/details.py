import streamlit as st  # type: ignore
import requests
import psycopg2
from streamlit_extras.switch_page_button import switch_page  # type: ignore

# --- PAGE CONFIG ---
st.set_page_config(page_title="SweetSpot - User Details", page_icon="🍰", layout="wide")

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

def get_customer_details(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, email, address, phone_no FROM sweetspot_app_customer WHERE email = %s", (email,))
    customer_details = cursor.fetchone()
    cursor.close()
    conn.close()
    return customer_details if customer_details else None

# --- PROFILE PAGE ---
st.title("Profile Details")

user_first_name = st.session_state.user_info.get('first_name', 'User')
user_email = st.session_state.user_info.get('email', 'Not Provided')

st.subheader(f"Welcome, {user_first_name}!")
st.write(f"Email: {user_email}")

# --- Fetching and Displaying Additional User Information ---
customer_details = get_customer_details(user_email)

if customer_details:
    first_name, last_name, email, address, phone_number = customer_details
else:
    st.write("Could not fetch customer details.")

# --- Styling the Profile Details Box ---
def load_custom_css():
    st.markdown("""
    <style>
        /* General body styling */
        body {
            background-color: #f4f7fb;
            font-family: 'Arial', sans-serif;
        }

        /* Profile box styling */
        .profile-box {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 30px;
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
        }

        .profile-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2);
        }

        /* Title styling */
        .profile-title {
            font-size: 2rem;
            font-weight: bold;
            color: #f76c6c;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: color 0.3s ease;
        }

        .profile-title:hover {
            color: #ff6b6b;
        }

        /* Profile details styling */
        .profile-detail {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #333;
            transition: color 0.3s ease;
            max-width: 100%;
            width: 100%;
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }

        .profile-detail:hover {
            color: #f76c6c;
            background-color: #ffe1e1;
        }

        .profile-label {
            font-weight: bold;
            color: #444;
        }

        .profile-value {
            color: #666;
        }

        /* Specific styling for address */
        .address {
            font-size: 1rem;
            color: #666;
            font-style: italic;
        }

        /* Phone number styling */
        .phone {
            font-size: 1.1rem;
            color: #4CAF50;
            font-weight: bold;
        }

        /* Log Out Button Styling */
        .logout-button {
            background-color: #f76c6c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: 30px;
        }

        .logout-button:hover {
            background-color: #ff6b6b;
        }
    </style>
    """, unsafe_allow_html=True)

# Load custom CSS for advanced styling
load_custom_css()

# --- Display the User Profile in a Styled Box ---
if customer_details:
    st.markdown(f'<p class="profile-title">Personal Information</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-detail"><span class="profile-label">Name:</span> <span class="profile-value">{first_name} {last_name}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-detail"><span class="profile-label">Email:</span> <span class="profile-value">{email}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-detail address"><span class="profile-label">Address:</span> <span class="profile-value">{address}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-detail phone"><span class="profile-label">Phone Number:</span> <span class="profile-value">{phone_number}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Optionally, add a logout button with custom styling
if st.button("Log Out", key="logout_button"):
    st.session_state.clear()
    switch_page("app")  # Redirect to the login page after logout
