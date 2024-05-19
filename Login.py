import hmac
import streamlit as st

def check_password():
    """Returns `True` if the user entered the correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and \
           hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    
    # Return True if the username and password are validated
    if st.session_state.get("password_correct", False):
        return True
    
    # Show login form
    login_form()
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("User not known or password incorrect")
    return False

if not check_password():
    st.stop()

# Main Streamlit app starts here
st.write("Welcome to the app!")
st.button("Click me")
