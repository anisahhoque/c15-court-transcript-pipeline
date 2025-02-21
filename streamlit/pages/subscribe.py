"""Page to subscribe using email to daily judgment reports."""
from os import environ as ENV

import streamlit as st

from subscribe_functions import is_valid_email, create_client, create_contact

def main():
    """Main function to run subscribe page."""
    email_input = st.text_input("Enter your email here: ")
    if st.button("Subscribe to daily judgment emails"):
        if is_valid_email(email_input.strip()):
            ses_client = create_client(ENV["ACCESS_KEY"], ENV["SECRET_KEY"]) 
            create_contact(ses_client, ENV["CONTACT_LIST_NAME"], email_input.strip())
        else:
            st.error("Please ensure your email is valid.")


if __name__ == "__main__":
    main()