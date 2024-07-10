import streamlit as st

from vnstock import (
    listing_companies as _listing_companies,
)

@st.cache_data
def listing_companies():
    return _listing_companies()