import streamlit as st

st.set_page_config(
    page_title="Front Page"
)

st.write("# Welcome to my web scraping project!")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    **Select a page from the sidebar** for demos
    """
)