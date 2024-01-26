import streamlit as st
import all_pages
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Set Streamlit page configuration
st.set_page_config(
    page_title="Annotator",
    page_icon="🖋️",
)

# Load configuration from YAML file
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create an authenticator instance
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Generate hashed passwords
hashed_passwords = stauth.Hasher(['fuseadmin', 'fuseuser']).generate()

# User authentication
name, authentication_status, username = authenticator.login('Login', 'main')

# Handle authentication status
if authentication_status:
    col1,col2,col3=st.columns(3)
    with col3:
        authenticator.logout('Logout', 'main')

    # Determine user type and render appropriate pages
    if name.lower() == 'admin':
        all_pages.render_admin_pages(name)
    elif name.lower() == 'user':
        all_pages.render_user_pages(name)

elif authentication_status is False:
    st.error('Username/password is incorrect')

elif authentication_status is None:
    st.warning('Please enter your username and password')
