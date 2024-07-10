import streamlit as st

from vnstock import (
    stock_intraday_data,
)


def get_transaction_today(symbol, size=None, cache=False):
    
    @st.cache_data
    def get_transaction_today_cache(symbol, size):
        return stock_intraday_data(symbol, page_size=size, investor_segment=True)
    
    if cache:
        return get_transaction_today_cache(symbol, size)

    return stock_intraday_data(symbol, page_size=size, investor_segment=True)