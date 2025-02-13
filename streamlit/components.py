import streamlit as st


def dashboard_title():
    st.title("Judgment Reader")

    # Sidebar with 3 pages
    page = st.sidebar.radio(
        'Select a page', ['Home', 'Judgment Search', 'Analytics'])

    # Centered subheader with dynamic content based on selected page
    st.markdown(
        f"""
        <h2 style="text-align: center;">{page} Page</h2>
        """,
        unsafe_allow_html=True
    )

    return page
