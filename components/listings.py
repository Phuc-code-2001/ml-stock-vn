from utils.companies import listing_companies
import streamlit as st

def render_select_company():
    symbol = st.selectbox("Chọn mã cổ phiếu", listing_companies(), index=None)
    return symbol