import streamlit as st
import datetime as dt
from licenses import accept_licence
accept_licence()

from components.listings import render_select_company
from components.transactions import render_transaction_today, render_select_symbol_history_day, render_save_transactions
from components.timing import render_time

sidebar = st.sidebar
sidebar.write("## Thông tin")
sidebar.write("Ứng dụng này giúp bạn xem thông tin giao dịch cổ phiếu trong ngày")
sidebar.write("Dữ liệu được cung cấp bởi VNDIRECT")
sidebar.write("## Hướng dẫn")
sidebar.write("Chọn mã cổ phiếu từ danh sách bên dưới")
sidebar.write("Chọn nhà đầu tư để xem thông tin giao dịch của họ")
sidebar.write("## Liên hệ")
sidebar.write("Liên hệ với tác giả qua email: itphuc892@gmail.com")

gmt_vn_time = dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(hours=7)
# render_time(lambda: dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(hours=7), widget=sidebar)
if gmt_vn_time.hour > 15:
    expanded = sidebar.expander("Cập nhật dữ liệu")
    render_save_transactions(expanded)


symbol = render_select_company()
if symbol:
    selected_date = render_select_symbol_history_day(symbol)
    if st.button("Reload", key="Reload"): st.rerun()
    render_transaction_today(symbol, selected_date)
else:
    st.write("Chọn mã cổ phiếu để xem thông tin giao dịch")