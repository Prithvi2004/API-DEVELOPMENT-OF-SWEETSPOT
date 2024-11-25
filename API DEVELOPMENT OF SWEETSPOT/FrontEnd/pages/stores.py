import streamlit as st  # type: ignore
import os
import psycopg2
from streamlit_extras.switch_page_button import switch_page  # type: ignore

# --- PAGE CONFIG ---
st.set_page_config(page_title="SweetSpot - Stores", page_icon="🏪", layout="wide")

# --- SESSION CHECK ---
if 'user_info' not in st.session_state or st.session_state.user_info is None:
    st.warning("Please log in to access the stores page.")
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

# --- Function to Fetch Stores ---
def get_stores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, city, address, contact_number, email, description
        FROM sweetspot_app_store
    """)
    stores = cursor.fetchall()
    cursor.close()
    conn.close()
    return stores

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    /* General Font Styling */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    * {
        font-family: 'Roboto', sans-serif;
    }

    /* Title Styling */
    .stTitle {
        color: #1d3557;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        text-align: center;
    }

    /* Container for Store Cards */
    .store-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
        max-width: 900px;
        margin: auto;
    }

    /* Store Card Styling */
    .store-card {
        background: #ffffff;
        border-radius: 15px;
        box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.1);
        width: 100%;
        display: flex;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        overflow: hidden;
    }

    /* Card Hover Effect */
    .store-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
    }

    /* Image Container */
    .store-image-container {
        flex: 1;
        max-width: 300px;
        overflow: hidden;
    }

    /* Image Styling */
    .store-image {
        width: 100%;
        height: auto;  /* Ensures image maintains its aspect ratio */
        object-fit: cover;
        transition: transform 0.3s ease;
    }

    .store-card:hover .store-image {
        transform: scale(1.05);
    }

    /* Store Info Container */
    .store-info {
        flex: 2;
        padding: 1.5rem;
    }

    /* Store Name Styling */
    .store-title {
        color: #1d3557;
        font-size: 1.8em;
        font-weight: 700;
        margin-bottom: 0.5em;
    }

    /* Store Content Styling */
    .store-content {
        color: #555;
        font-size: 1em;
        line-height: 1.6;
    }

    /* Highlighted Text */
    .highlight {
        color: #e63946;
        font-weight: 600;
    }

    /* Button Styling */
    .store-button {
        display: inline-block;
        margin-top: 1em;
        padding: 0.5em 1.5em;
        background-color: #457b9d;
        color: #ffffff;
        text-decoration: none;
        border-radius: 5px;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }

    .store-button:hover {
        background-color: #1d3557;
    }
    </style>
""", unsafe_allow_html=True)


# --- STORES PAGE ---
st.title("Our Stores")

user_first_name = st.session_state.user_info.get('first_name', 'User')
st.subheader(f"Welcome, {user_first_name}!")  # Shows the first name of the user

# Fetch store details from the database
stores = get_stores()

# Display stores with custom styling
st.markdown('<div class="store-container">', unsafe_allow_html=True)

# --- Explicitly Define Each Store Card (with Dynamic Data) ---
for store in stores:
    store_id, name, city, address, contact_number, email, description = store

    # Define image URLs explicitly for each store
    if store_id == 1:
        store_image_url = "https://cdn.glitch.global/635bd00a-27f6-4386-bf2e-68d26590e927/store_1.webp?v=1731503706512"
    elif store_id == 2:
        store_image_url = "https://cdn.glitch.global/635bd00a-27f6-4386-bf2e-68d26590e927/2.jpeg?v=1731503919206"
    elif store_id == 3:
        store_image_url = "https://cdn.glitch.global/635bd00a-27f6-4386-bf2e-68d26590e927/3.jpeg?v=1731503926106"
    else:
        store_image_url = "https://cdn.glitch.global/635bd00a-27f6-4386-bf2e-68d26590e927/store_1.webp?v=1731503706512"  # Default fallback image

    # Manually display the image and store details using HTML
    st.markdown(f"""
    <div class="store-card">
        <div class="store-image-container">
            <img src="{store_image_url}" alt="{name} Image" class="store-image"/>
        </div>
        <div class="store-info">
            <div class="store-title">{name}</div>
            <div class="store-content">
                <p><span class="highlight">Location:</span> {city}</p>
                <p><span class="highlight">Address:</span> {address}</p>
                <p><span class="highlight">Contact:</span> {contact_number}</p>
                <p><span class="highlight">Email:</span> {email}</p>
                <p>{description}</p>
            </div>
            <a href="#" class="store-button">View Details</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
