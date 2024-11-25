import streamlit as st  # type: ignore
import requests
import psycopg2
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="SweetSpot - Dashboard", page_icon="🍰", layout="wide")

# --- SESSION CHECK ---
if 'user_info' not in st.session_state or st.session_state.user_info is None:
    st.warning("Please log in to access the dashboard.")
    st.stop()

# --- DATABASE CONNECTION FUNCTIONS ---

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname='sweetspotdb',
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port='5432'
    )
    return conn

def get_customer_id(email):
    """Fetch customer ID based on email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sweetspot_app_customer WHERE email = %s", (email,))
    customer_id = cursor.fetchone()
    cursor.close()
    conn.close()
    return customer_id[0] if customer_id else None

def get_distance(customer_id):
    """Fetch distance and duration for an order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sweetspot_app_order WHERE customer_id = %s", (customer_id,))
    order_id = cursor.fetchone()
    
    if order_id:
        cursor.execute("SELECT distance, duration FROM sweetspot_app_order WHERE id = %s", (order_id[0],))
        result = cursor.fetchone()
    else:
        result = None
    return result if result else (None, None)

# --- CAKES PAGE UI COMPONENTS ---

# Title and greeting
st.title("Cakes and Customization")
user_first_name = st.session_state.user_info.get('first_name', 'User')
st.subheader(f"Welcome, {user_first_name}!")  # Display user first name

# --- Custom CSS Styling ---
def load_custom_css():
    """Load custom CSS styles for cake display."""
    st.markdown("""
    <style>
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

        .cake-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        .cake-image {
            border-radius: 10px;
            width: 150px;
            height: 150px;
            object-fit: cover;
            margin-bottom: 15px;
        }

        .cake-name {
            font-weight: bold;
            font-size: 1.2rem;
            color: #f76c6c;
            margin-bottom: 5px;
        }

        .cake-price {
            font-size: 1rem;
            color: #333333;
            margin-bottom: 10px;
        }

        .cake-description {
            font-size: 0.9rem;
            color: #666666;
        }
    </style>
    """, unsafe_allow_html=True)

# Load custom CSS
load_custom_css()

# Fetch customer ID using the email from session state
customer_email = st.session_state.user_info['email']
customer_id = get_customer_id(customer_email)

# --- Cart Management Functions ---

def get_cart(customer_id):
    """Fetch the current cart for the customer."""
    url = f"http://127.0.0.1:8000/api/carts/"
    response = requests.get(url, params={"customer": customer_id})

    if response.status_code == 200:
        carts = response.json()  # List of carts
        if carts:  # If carts exist, return the first one
            return carts[0]
        else:
            return None
    else:
        st.error(f"Failed to fetch cart information: {response.json()}")
        return None

def add_item_to_cart(cart_id, cake_id, quantity, customization, store_id):
    """Add a cake item to the cart."""
    url = f"http://127.0.0.1:8000/api/carts/{cart_id}/add_item/"
    response = requests.post(url, json={
        "cake_id": cake_id,
        "quantity": quantity,
        "customization": customization,
        "store_id": store_id  # Include the store ID in the request
    })
    if response.status_code == 200:
        return True
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return False


# --- Fetch Available Cakes ---

def get_available_cakes():
    """Fetch available cakes from the selected store."""
    url = f"http://127.0.0.1:8000/api/cakes/"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Assuming the API returns a list of cakes
    else:
        st.error(f"Failed to fetch cakes: {response.text}")
        return []

# --- Initialize Cart ---
cart = get_cart(customer_id)
if cart is None:
    st.warning("No cart found. You can create a cart below.")
else:
    st.success("Cart found!")

# --- Create Cart Button ---
if st.button("Create Cart"):
    if cart is None:  # Only create a cart if one does not already exist
        create_cart_url = "http://127.0.0.1:8000/api/carts/"
        response = requests.post(create_cart_url, json={"customer": customer_id})
        if response.status_code == 201:
            cart = response.json()  # Update the cart variable
            st.success("Cart created successfully!")
        else:
            st.error(f"Failed to create cart: {response.json()}")
    else:
        st.warning("A cart already exists for this customer!")

# --- Store Selection Dropdown ---
stores = [
    {"id": 1, "name": "SweetSpot @Kovvada"},
    {"id": 2, "name": "SweetSpot @Undi"},
    {"id": 3, "name": "SweetSpot @Tadepalligudem"}
]

store_options = {store["name"]: store["id"] for store in stores}
selected_store = st.selectbox("Choose a Store", options=list(store_options.keys()))
selected_store_id = store_options[selected_store]  # Store ID for the selected store


# Fetch cakes related to the selected store
cakes = get_available_cakes()

# --- Show Cakes Button --- 
if 'show_cakes' not in st.session_state:
    st.session_state.show_cakes = False

# --- Toggle Cake Visibility ---
if st.button("Show Available Cakes"):
    st.session_state.show_cakes = True

if st.button("Hide Cakes"):
    st.session_state.show_cakes = False

# --- Display Cakes if Flag is Set ---
if st.session_state.show_cakes:
    if cakes:
        # Determine the starting index for the cakes based on the selected store
        if selected_store == "SweetSpot @Kovvada":
            start_idx = 0
        elif selected_store == "SweetSpot @Undi":
            start_idx = 5
        elif selected_store == "SweetSpot @Tadepalligudem":
            start_idx = 10

        # Slice cakes to show only 5 cakes per store
        selected_cakes = cakes[start_idx:start_idx + 5]
        
        st.write(f"Here are the available cakes from {selected_store}:")  # Show selected store name

        # Loop through cakes and create side-by-side columns layout
        cols = st.columns(3)  # Display 3 cakes per row
        
        for i, cake in enumerate(selected_cakes):
            col = cols[i % 3]  # Arrange cakes in columns
            
            with col:
                # Cake card display with image and details
                st.markdown(f"""
                <div class="cake-card">
                    <img src="{cake['image']}" alt="{cake['name']}" class="cake-image" />
                    <div class="cake-name">{cake['name']}</div>
                    <div class="cake-price">Price: ₹{cake['price']}</div>
                    <div class="cake-description">Flavor: {cake['flavour']}</div>
                    <div class="cake-description">Size: {cake['size']}</div>
                    <div class="cake-description">Available: {'✅' if cake['available'] else '❌'}</div>
                    <div class="cake-description">{cake['description']}</div>
                    <div class="cake-description">{cake['id']}</div>
                </div>
                """, unsafe_allow_html=True)

                # Input fields for adding to cart
                quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1, key=f"quantity_{cake['id']}")
                customization = {
                    "message": st.text_input("Customization Message", key=f"message_{cake['id']}"),
                    "egg_version": st.checkbox("Egg Version", value=True, key=f"egg_{cake['id']}"),
                    "toppings": st.text_input("Toppings", key=f"toppings_{cake['id']}"),
                    "shape": st.selectbox("Shape", options=["Round", "Square", "Heart"], index=0, key=f"shape_{cake['id']}")
                }

                # Add to cart button
                if st.button(f"Add {cake['name']} to Cart", key=f"add_{cake['id']}"):
                    if add_item_to_cart(cart['id'], cake['id'], quantity, customization, selected_store_id):
                        st.success(f"{cake['name']} added to cart from {selected_store}!")
                    else:
                        st.error("Failed to add item to cart.")

    else:
        st.warning("No cakes are available at the moment.")
