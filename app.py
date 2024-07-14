import streamlit as st
from licenses import accept_licence
accept_licence()

from components.listings import render_select_company
from components.transactions import render_transaction_today


sidebar = st.sidebar
with sidebar:
    st.write("## Thông tin")
    st.write("Ứng dụng này giúp bạn xem thông tin giao dịch cổ phiếu trong ngày")
    st.write("Dữ liệu được cung cấp bởi VNDIRECT")
    st.write("## Hướng dẫn")
    st.write("Chọn mã cổ phiếu từ danh sách bên dưới")
    st.write("Chọn nhà đầu tư để xem thông tin giao dịch của họ")
    st.write("## Liên hệ")
    st.write("Liên hệ với tác giả qua email: itphuc892@gmail.com")

symbol = render_select_company()
if symbol:
    render_transaction_today(symbol)
else:
    st.write("Chọn mã cổ phiếu để xem thông tin giao dịch")