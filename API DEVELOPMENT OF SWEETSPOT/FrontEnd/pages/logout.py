# pages/logout.py

import streamlit as st # type: ignore
from streamlit_extras.switch_page_button import switch_page # type: ignore

# Set the title for the logout page
st.title("Logging Out...")

# Clear the user_info from session state to log out
st.session_state.user_info = None

# Display success message
st.success("You have been logged out.")

# Set the page to 'login' to navigate to the login page
if st.button("Go to Login Page"):
    switch_page("app")  
