import streamlit as st  # type: ignore
import requests
import psycopg2

# --- PAGE CONFIG ---
st.set_page_config(page_title="SweetSpot - Cart and Order", page_icon="🍰", layout="wide")

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

# --- Function to Fetch Cart ---
def get_cart(customer_id):
    url = f"http://127.0.0.1:8000/api/carts/"
    response = requests.get(url, params={"customer": customer_id})

    if response.status_code == 200:
        carts = response.json()
        return carts[0] if carts else None
    else:
        st.error(f"Failed to fetch cart information: {response.json()}")
        return None

# --- Function to Fetch Cake Details ---
def get_cake_details(cake_id):
    url = f"http://127.0.0.1:8000/api/cakes/{cake_id}/"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch cake details for cake ID {cake_id}: {response.text}")
        return None

# --- Function to Place Order ---
def place_order(order_data):
    url = "http://127.0.0.1:8000/api/orders/place_order/"
    response = requests.post(url, json=order_data)
    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Failed to place order: {response.text}")
        return None

# --- Advanced CSS Styling with Animations ---
def load_custom_css():
    st.markdown("""
    <style>
        /* Page Styling */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f7fc;
        }

        /* Cart Item Styling */
        .cart-item {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .cart-item:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .cart-item img {
            border-radius: 8px;
            width: 100px;
            height: 100px;
            object-fit: cover;
            margin-right: 15px;
        }

        .cart-item-details {
            flex-grow: 1;
            animation: fadeIn 1s ease-in-out;
        }

        /* Fade In Animation */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .cart-item-details h4 {
            margin: 0;
            font-size: 1.1em;
            color: #333;
            font-weight: bold;
        }

        .cart-item-details p {
            margin: 5px 0;
            color: #666;
        }

        /* Total Amount Styling */
        .cart-total {
            font-size: 1.2em;
            font-weight: bold;
            color: #f76c6c;
            text-align: right;
            margin-top: 10px;
        }

        /* Button Styling with Animation */
        .stButton>button {
            background-color: #f76c6c;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #f55555;
        }

        /* Payment Method Dropdown Styling */
        .stSelectbox {
            margin-top: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# --- CART PAGE ---
st.title("Cart and Place Order")
user_first_name = st.session_state.user_info.get('first_name', 'User')
st.subheader(f"Welcome, {user_first_name}!")

# --- Fetch customer ID using the email from session state ---
customer_email = st.session_state.user_info['email']
customer_id = get_customer_id(customer_email)

# --- Initialize Cart ---
cart = get_cart(customer_id)

# --- CART PAGE --- 
if cart:
    st.success("Cart found! Let's review your items.")
    if st.button("View Cart"):
        if 'items' in cart and cart['items']:
            st.write("Your Cart:")
            def get_store_name(cake_id):
                if 1 <= cake_id <= 5:
                    return "SweetSpot @Kovvada"
                elif 6 <= cake_id <= 10:
                    return "SweetSpot @Undi"
                elif 11 <= cake_id <= 15:
                    return "SweetSpot @Tadepalligudem"
                else:
                    return "Unknown Store"

            for item in cart['items']:
                cake_details = get_cake_details(item['cake']) if isinstance(item['cake'], int) else item['cake']
                if cake_details:
                    store_name = get_store_name(item['cake'])                    
                    st.markdown(f"""
                    <div class="cart-item">
                        <img src="{cake_details.get('image', '')}" alt="{cake_details.get('name', 'Cake')}">
                        <div class="cart-item-details">
                            <h4>{cake_details.get('name', 'Cake')}</h4>
                            <p>Flavor: {cake_details.get('flavour', 'N/A')}</p>
                            <p>Size: {cake_details.get('size', 'N/A')}</p>
                            <p>Price: ₹{cake_details.get('price', 'N/A')}</p>
                            <p>Description: {cake_details.get('description', 'No description available')}</p>
                            <p>Quantity: {item['quantity']}</p>
                            <p>Subtotal: ₹{item['subtotal']}</p>
                            <p><strong>Store:</strong> {store_name}</p>  <!-- Display Store -->
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"<div class='cart-total'>Total Amount: ₹{cart['total_amount']}</div>", unsafe_allow_html=True)
        else:
            st.warning("Your cart is empty.")
else:
    st.warning("No cart found. Please add items to your cart first.")

# --- Separate Place Order Section ---
if cart and 'items' in cart and cart['items']:
    st.subheader("Payment Information")
    payment_method = st.selectbox("Select Payment Method", ["card", "cash"])

    if payment_method == "card":
        card_number = st.text_input("Card Number", type="password", placeholder="Enter card number")
        card_holder_name = st.text_input("Card Holder Name", placeholder="Enter card holder name")
        expiration_date = st.date_input("Expiration Date")
        cvv = st.text_input("CVV", type="password", placeholder="Enter CVV")

    if st.button("Place Order"):
        if payment_method == "card":
            if not card_number or not card_holder_name or not expiration_date or not cvv:
                st.error("Please fill in all card details.")

            card_details = {
                "card_number": card_number,
                "card_holder_name": card_holder_name,
                "expiration_date": expiration_date.isoformat(),  
                "cvv": cvv
            }
        else:
            card_details = {}

        order_data = {
            "customer_id": customer_id,
            "payment_method": payment_method,
            "card_details": card_details
        }
        order_response = place_order(order_data)
        if order_response:
            st.balloons()  
            st.success("Order placed successfully!")
            # st.write("Order Details:", order_response)
        else:
            st.error("Failed to place order.")
else:
    st.warning("Your cart is empty, unable to place order.")