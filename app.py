import streamlit as st 
import all_pages
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="Annotator",
    page_icon="🖋️",
)

with open('./config.yaml') as file:
    config=yaml.load(file,Loader=SafeLoader)

#print(config)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

hashed_passwords = stauth.Hasher(['fuseadmin', 'fuseuser']).generate()
print(hashed_passwords)
#print(config['credentials'])

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status:
    authenticator.logout('Logout','main')
    print(name)
    if name.lower()=='admin':
        all_pages.render_admin_pages(name)
    elif name.lower()=='user':
        all_pages.render_user_pages(name)

elif authentication_status==False:
    st.error('Username/password is incorrect ')
elif authentication_status==None:
    st.warning('Please enter your username and password')

