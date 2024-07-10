import streamlit as st
import datetime as dt

from utils.companies import listing_companies
from utils.transactions import get_transaction_today
from utils.formaters import hightlight_type, hightlight_investor

import numpy as np
import pandas as pd

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

if "symbol" in st.session_state:
    default_symbol = st.session_state.symbol
else:
    default_symbol = "FPT"

symbol = st.selectbox('Chọn mã cổ phiếu:', listing_companies(), index=listing_companies().ticker.to_list().index(default_symbol))
st.session_state.symbol = symbol

trading_df = get_transaction_today(symbol, size=10000, cache=True)
trading_df.columns = ["symbol", "time", "type", "investor", "volume", "price", "count", "change"]
trading_df = trading_df[["time", "type", "investor", "volume", "price"]]

trading_df["value"] = trading_df["volume"].values * trading_df["price"].values
trading_df["type"] = trading_df["type"].map({"Buy Up": "BUY", "Sell Down": "SELL"})
# convert all number columns to int
trading_df["volume"] = trading_df["volume"].astype(int)
trading_df["price"] = trading_df["price"].astype(int)
trading_df["value"] = trading_df["value"].astype(int)

buyup = trading_df[trading_df["type"] == "BUY"]
selldown = trading_df[trading_df["type"] == "SELL"]

buyup_value = buyup["value"].sum()
selldown_value = selldown["value"].sum()

buy_volume = buyup["volume"].sum()
sell_volume = selldown["volume"].sum()

total_volume = buy_volume + sell_volume
total_value = buyup_value + selldown_value

st.write(f"Thống kê giao dịch của mã {symbol} ngày {dt.datetime.now().strftime('%d/%m/%Y')}")
st.write(f"Tổng cộng: {len(trading_df):,} giao dịch")
st.write(f"Tổng khối lượng: {int(total_volume):,} đơn vị")
st.write(f"Tổng giá trị: {total_value:,} VND")
# put a horizontal line
st.write('---')
l1, r1 = st.columns(2)
with l1:    
    st.write(f"Số lượng giao dịch mua: {len(buyup):,}")
    st.write(f"Tổng khối lượng mua: {buy_volume:,} đơn vị")
    st.write(f"Tổng giá trị mua: {buyup_value:,} VND")

with r1:
    st.write(f"Số lượng giao dịch bán: {len(selldown):,}")
    st.write(f"Tổng khối lượng bán: {sell_volume:,} đơn vị")
    st.write(f"Tổng giá trị bán: {selldown_value:,} VND")

# put a horizontal line
st.write("---")

investor = st.selectbox('Chọn nhà đầu tư:', ["ALL", "SHARK", "WOLF", "SHEEP"])

l2, r2 = st.columns(2)
with l2:
    start_time = st.time_input("Bắt đầu:", dt.time(9, 0))

with r2:
    end_time = st.time_input("Kết thúc:", dt.time(15, 45))

trading_df.time = pd.to_datetime(trading_df.time, format='%H:%M:%S')
filterd_df = trading_df[(trading_df.time >= pd.to_datetime(start_time.strftime('%H:%M:%S'), format='%H:%M:%S')) & 
                        (trading_df.time <= pd.to_datetime(end_time.strftime('%H:%M:%S'), format='%H:%M:%S'))]
filterd_df["time"] = filterd_df["time"].map(lambda x: x.strftime('%H:%M:%S'))
filterd_df = (filterd_df[filterd_df["investor"] == investor] if investor != "ALL" else filterd_df)

# make unique datetime index
filterd_df = filterd_df.reset_index(drop=True)
filterd_df["time"] = [ str(i) + " - " + filterd_df.loc[i, "time"] for i in filterd_df.index]
filterd_df = filterd_df.set_index("time", drop=True)
styled_df = filterd_df.style.apply(hightlight_type, subset=['type']) \
                            .apply(hightlight_investor, subset=['investor']) \
                            .format(precision=3, thousands=".", decimal=",")

l3, r3 = st.columns(2)
with l3:

    st.dataframe(
        styled_df,
    )

with r3:

    if investor == "ALL" or investor == "SHARK":
        st.write("Thống kê nhà đầu tư cá mập")
        shark_df = trading_df[trading_df["investor"] == "SHARK"]

        shark_buy = shark_df[shark_df["type"] == "BUY"]
        shark_sell = shark_df[shark_df["type"] == "SELL"]

        shark_buy_volume = shark_buy["volume"].sum()
        shark_sell_volume = shark_sell["volume"].sum()
        shark_diff_volume = shark_buy_volume - shark_sell_volume

        shark_buy_value = shark_buy["value"].sum()
        shark_sell_value = shark_sell["value"].sum()
        shark_diff_value = shark_buy_value - shark_sell_value

        shark_buy_price = shark_buy_value / shark_buy_volume
        shark_sell_price = shark_sell_value / shark_sell_volume

        shark_diff_price = shark_diff_value / shark_diff_volume

        shark_summary = pd.DataFrame({
            "Loại": ["M", "B", "M-B"],
            "Giá (nghìn)": [shark_buy_price / 1e3, shark_sell_price / 1e3, shark_diff_price / 1e3],
            "Khối lượng (nghìn)": [shark_buy_volume / 1e3, shark_sell_volume / 1e3, shark_diff_volume / 1e3],
            "Giá trị (tỷ)": [shark_buy_value / 1e9, shark_sell_value / 1e9, shark_diff_value / 1e9]
        }).set_index("Loại")
        st.table(shark_summary.style.format(precision=2, thousands=".", decimal=","))

    if investor == "ALL" or investor == "WOLF":
        st.write("Thống kê nhà đầu tư sói")
        wolf_df = trading_df[trading_df["investor"] == "WOLF"]

        wolf_buy = wolf_df[wolf_df["type"] == "BUY"]
        wolf_sell = wolf_df[wolf_df["type"] == "SELL"]

        wolf_buy_volume = wolf_buy["volume"].sum()
        wolf_sell_volume = wolf_sell["volume"].sum()
        wolf_diff_volume = wolf_buy_volume - wolf_sell_volume

        wolf_buy_value = wolf_buy["value"].sum()
        wolf_sell_value = wolf_sell["value"].sum()
        wolf_diff_value = wolf_buy_value - wolf_sell_value

        wolf_buy_price = wolf_buy_value / wolf_buy_volume
        wolf_sell_price = wolf_sell_value / wolf_sell_volume

        wolf_diff_price = wolf_diff_value / wolf_diff_volume

        wolf_summary = pd.DataFrame({
            "Loại": ["M", "B", "M-B"],
            "Giá (nghìn)": [wolf_buy_price / 1e3, wolf_sell_price / 1e3, wolf_diff_price / 1e3],
            "Khối lượng (nghìn)": [wolf_buy_volume / 1e3, wolf_sell_volume / 1e3, wolf_diff_volume / 1e3],
            "Giá trị (tỷ)": [wolf_buy_value / 1e9, wolf_sell_value / 1e9, wolf_diff_value / 1e9]
        }).set_index("Loại")
        st.table(wolf_summary.style.format(precision=2, thousands=".", decimal=","))

    if investor == "ALL" or investor == "SHEEP":
        st.write("Thống kê nhà đầu tư cừu")
        sheep_df = trading_df[trading_df["investor"] == "SHEEP"]

        sheep_buy = sheep_df[sheep_df["type"] == "BUY"]
        sheep_sell = sheep_df[sheep_df["type"] == "SELL"]

        sheep_buy_volume = sheep_buy["volume"].sum()
        sheep_sell_volume = sheep_sell["volume"].sum()
        sheep_diff_volume = sheep_buy_volume - sheep_sell_volume

        sheep_buy_value = sheep_buy["value"].sum()
        sheep_sell_value = sheep_sell["value"].sum()
        sheep_diff_value = sheep_buy_value - sheep_sell_value

        sheep_buy_price = sheep_buy_value / sheep_buy_volume
        sheep_sell_price = sheep_sell_value / sheep_sell_volume

        sheep_diff_price = sheep_diff_value / sheep_diff_volume

        sheep_summary = pd.DataFrame({
            "Loại": ["M", "B", "M-B"],
            "Giá (nghìn)": [sheep_buy_price / 1e3, sheep_sell_price / 1e3, sheep_diff_price / 1e3],
            "Khối lượng (nghìn)": [sheep_buy_volume / 1e3, sheep_sell_volume / 1e3, sheep_diff_volume / 1e3],
            "Giá trị (tỷ)": [sheep_buy_value / 1e9, sheep_sell_value / 1e9, sheep_diff_value / 1e9]
        }).set_index("Loại")
        st.table(sheep_summary.style.format(precision=2, thousands=".", decimal=","))
