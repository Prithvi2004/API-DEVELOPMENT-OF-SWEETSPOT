#app.py
import streamlit as st  # type: ignore
import requests
import psycopg2
import os
from streamlit_extras.switch_page_button import switch_page  # type: ignore
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="SweetSpot - Login", page_icon="🍰", layout="wide")

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

def get_user_name(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM sweetspot_app_customer WHERE email = %s", (email,))
    user_name = cursor.fetchone()
    cursor.close()
    conn.close()
    return user_name[0] if user_name else None

# --- STYLING ---
def load_css():
    st.markdown("""
    <style>
        body {
            font-family: 'Open Sans', sans-serif;
        }
        header, footer {
            visibility: hidden;
        }
        .main {
            background-color: #f9f9f9;
        }
        .stButton button {
            background-color: #f76c6c;
            border-radius: 10px;
            color: white;
        }
        .stButton button:hover {
            background-color: #ff4b4b;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- LOAD ASSETS ---
logo_path = os.path.join("assets", "sweetspot.png")
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=200)

# --- BACKEND FUNCTION INTEGRATION ---
def login(email, password):
    url = "http://127.0.0.1:8000/api/customers/login/" 
    response = requests.post(url, json={"email": email, "password": password})
    if response.status_code == 200:
        user_data = get_user_name(email)
        customer_id = response.json().get('id')  # Assuming the response contains the customer ID
        return {
            "first_name": user_data,
            "email": email,
            "customer_id": customer_id  # Include customer ID in the return data
        }
    else:
        return None

def signup(data):
    url = "http://127.0.0.1:8000/api/customers/" 
    response = requests.post(url, json=data)
    return response.status_code == 201

# --- LOGIN/SIGNUP PAGE ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

if st.session_state.user_info is None:
    st.title("Welcome to SweetSpot 🍰")
    st.subheader("Delivering Delight to Your Doorstep!")

    col1, col2 = st.columns(2)

    # --- LOGIN FORM ---
    with col1:
        st.header("Login")
        email_login = st.text_input("Email Address")
        password_login = st.text_input("Password", type="password")

        if st.button("Login"):
            user_data = login(email_login, password_login)
            if user_data:
                st.session_state.user_info = user_data  
                st.success("Login Successful!")
                switch_page("dashboard")  
            else:
                st.error("Invalid credentials, please try again.")

    # --- SIGNUP FORM ---
    with col2:
        st.header("Sign Up")
        first_name = st.text_input("First Name", key="first_name")
        last_name = st.text_input("Last Name", key="last_name")
        email_signup = st.text_input("Email Address", key="email_signup")
        password_signup = st.text_input("Password", type="password", key="password_signup")
        phone_no = st.text_input("Phone Number", key="phone_no")
        address = st.text_area("Address", key="address")
        city = st.text_input("City", key="city")
        state = st.text_input("State", key="state")
        pincode = st.text_input("Pincode", key="pincode")

        if st.button("Sign Up"):
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email_signup,
                "password": password_signup,
                "phone_no": phone_no,
                "address": address,
                "city": city,
                "state": state,
                "pincode": pincode
            }
            if signup(user_data):
                st.success("Sign Up Successful! You can now log in.")
            else:
                st.error("Sign Up Failed. Please check the details and try again.")

else:
    st.success(f"Welcome back {st.session_state.user_info['first_name']}!")
    switch_page("dashboard")  

# --- FOOTER SECTION ---
st.markdown("""
    <hr style='border: 1px solid #f76c6c;' />
    <p style='text-align: center;'>© 2024 SweetSpot. All rights reserved.</p>
    """, unsafe_allow_html=True)