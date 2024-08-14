import streamlit as st
from licenses import accept_licence
accept_licence()

from components.listings import render_select_company
from components.transactions import render_transaction_today
from components.sidebar import render_sidebar

render_sidebar(st)
symbol = render_select_company()
if symbol:
    if st.button("Reload", key="Reload"): st.rerun()
    render_transaction_today(symbol, None)
else:
    st.write("Chọn mã cổ phiếu để xem thông tin giao dịch")