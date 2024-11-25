import streamlit as st  # type: ignore
import requests
import psycopg2

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

# Fetch customer ID using the email from session state
customer_email = st.session_state.user_info['email']
customer_id = get_customer_id(customer_email)

# --- Function to Fetch or Create Cart ---
def get_cart(customer_id):
    url = f"http://127.0.0.1:8000/api/carts/"
    response = requests.get(url, params={"customer": customer_id})

    if response.status_code == 200:
        carts = response.json()  # This is a list of carts
        if carts:  # Check if there are any carts
            return carts[0]  # Return the first cart
        else:
            return None
    else:
        st.error(f"Failed to fetch cart information: {response.json()}")
        return None

# --- Function to Add Item to Cart ---
def add_item_to_cart(cart_id, cake_id, quantity, customization):
    url = f"http://127.0.0.1:8000/api/carts/{cart_id}/add_item/"
    response = requests.post(url, json={
        "cake_id": cake_id,
        "quantity": quantity,
        "customization": customization
    })
    if response.status_code == 200:
        return True
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return False

# --- Function to Fetch Available Cakes ---
def get_available_cakes():
    url = "http://127.0.0.1:8000/api/cakes/"  # Django API endpoint for cakes
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Assuming the API returns a list of cakes
    else:
        st.error(f"Failed to fetch cakes: {response.text}")
        return []

# --- Function to Place Order ---
def place_order(order_data):
    url = "http://127.0.0.1:8000/api/orders/place_order/"
    response = requests.post(url, json=order_data)
    
    if response.status_code == 201:
        return response.json()  # Return the created order details
    else:
        st.error(f"Failed to place order: {response.text}")
        return None
