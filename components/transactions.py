import streamlit as st
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import os

from utils.transactions import get_transaction_today, get_transaction_on_date
from utils.enumtypes import InvestorType

from collections import defaultdict

from configs import UPDATE_DATA_PASSWORD

def render_transaction_today(symbol, selected_date=None):

    trading_df = get_transaction_today(symbol) if selected_date is None else get_transaction_on_date(symbol, selected_date)
    if selected_date is None:
        selected_date = dt.datetime.today().strftime('%d/%m/%Y')
    else:
        selected_date = dt.datetime.strptime(selected_date, "%Y-%m-%d").strftime('%d/%m/%Y')

    buy_df = trading_df[trading_df["match_type"] == "Buy"]
    sell_df = trading_df[trading_df["match_type"] == "Sell"]
    atc_df = trading_df[trading_df["match_type"] == "ATO/ATC"]

    buy_value = buy_df["value"].sum()
    sell_value = sell_df["value"].sum()

    buy_volume = buy_df["volume"].sum()
    sell_volume = sell_df["volume"].sum()

    total_volume = buy_volume + sell_volume
    total_value = buy_value + sell_value

    st.write(f"Thống kê giao dịch của mã {symbol} ngày {selected_date}")
    st.write(f"Tổng cộng: {len(trading_df):,} giao dịch")
    st.write(f"Tổng khối lượng: {int(total_volume):,} đơn vị")
    st.write(f"Tổng giá trị: {total_value:,} VND")
    st.write(f"Giá trung bình: {total_value / total_volume:,.0f} VND")
    # put a horizontal line
    st.write('---')

    rows = st.columns(3)

    rows[0].write(f"Mua: {len(buy_df):,} giao dịch")
    rows[0].write(f"Khối lượng: {buy_volume:,} đơn vị")
    rows[0].write(f"Tổng tiền: {buy_value:,.0f} VND")
    rows[0].write(f"Giá TB: {(buy_value / buy_volume):,.0f} VND")
        
    rows[1].write(f"Bán: {len(sell_df):,} giao dịch")
    rows[1].write(f"Khối lượng: {sell_volume:,} đơn vị")
    rows[1].write(f"Tổng tiền: {sell_value:,.0f} VND")
    rows[1].write(f"Giá TB: {(sell_value / sell_volume):,.0f} VND")

    rows[2].write(f"ATO/ATC: {len(atc_df):,} giao dịch")
    rows[2].write(f"Khối lượng: {atc_df['volume'].sum():,} đơn vị")
    rows[2].write(f"Tổng tiền: {atc_df['value'].sum():,.0f} VND")
    rows[2].write(f"Giá TB: {(atc_df['value'].sum() / (atc_df['volume'].sum() + 1e-9)):,.0f} VND")
        
    # put a horizontal line
    st.write("---")
    trading_df.time = pd.to_datetime(trading_df.time, format='mixed')

    rows = st.columns(2)
    # SHARK
    rows[0].write("Thống kê nhà đầu tư cá mập (> 5 tỷ)")
    shark_df = trading_df[trading_df["investor"] == InvestorType.SHARK.value]

    shark_buy = shark_df[shark_df["match_type"] == "Buy"]
    shark_sell = shark_df[shark_df["match_type"] == "Sell"]

    shark_buy_volume = shark_buy["volume"].sum()
    shark_sell_volume = shark_sell["volume"].sum()
    shark_diff_volume = shark_buy_volume - shark_sell_volume

    shark_buy_value = shark_buy["value"].sum()
    shark_sell_value = shark_sell["value"].sum()
    shark_diff_value = shark_buy_value - shark_sell_value

    shark_buy_price = shark_buy_value / (shark_buy_volume + 1e-9)
    shark_sell_price = shark_sell_value / (shark_sell_volume + 1e-9)

    shark_diff_price = shark_diff_value / (shark_diff_volume + 1e-9)

    shark_summary = pd.DataFrame({
        "Loại": ["M", "B", "M-B"],
        "Giá (nghìn)": [shark_buy_price / 1e3, shark_sell_price / 1e3, shark_diff_price / 1e3],
        "Khối lượng (nghìn)": [shark_buy_volume / 1e3, shark_sell_volume / 1e3, shark_diff_volume / 1e3],
        "Giá trị (tỷ)": [shark_buy_value / 1e9, shark_sell_value / 1e9, shark_diff_value / 1e9]
    }).set_index("Loại")
    rows[0].table(shark_summary.style.format(precision=2, thousands=".", decimal=","))

    if len(shark_buy):
        shark_buy_hist = defaultdict(int)
        for i in shark_buy.index:
            shark_buy_hist[shark_buy.price[i] / 1000] += shark_buy.volume[i] / 1000
        shark_buy_hist = pd.DataFrame(shark_buy_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        shark_buy_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="green", fontsize=18)
        rows[0].pyplot(fig)

    if len(shark_sell):
        shark_sell_hist = defaultdict(int)
        for i in shark_sell.index:
            shark_sell_hist[shark_sell.price[i] / 1000] += shark_sell.volume[i] / 1000
        shark_sell_hist = pd.DataFrame(shark_sell_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        shark_sell_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="red", fontsize=18)
        rows[0].pyplot(fig)

    # WOLF
    rows[1].write("Thống kê nhà đầu tư sói (> 1 tỷ)")
    wolf_df = trading_df[trading_df["investor"] == InvestorType.WOLF.value]

    wolf_buy = wolf_df[wolf_df["match_type"] == "Buy"]
    wolf_sell = wolf_df[wolf_df["match_type"] == "Sell"]

    wolf_buy_volume = wolf_buy["volume"].sum()
    wolf_sell_volume = wolf_sell["volume"].sum()
    wolf_diff_volume = wolf_buy_volume - wolf_sell_volume

    wolf_buy_value = wolf_buy["value"].sum()
    wolf_sell_value = wolf_sell["value"].sum()
    wolf_diff_value = wolf_buy_value - wolf_sell_value

    wolf_buy_price = wolf_buy_value / (wolf_buy_volume + 1e-9)
    wolf_sell_price = wolf_sell_value / (wolf_sell_volume + 1e-9)

    wolf_diff_price = wolf_diff_value / (wolf_diff_volume + 1e-9)

    wolf_summary = pd.DataFrame({
        "Loại": ["M", "B", "M-B"],
        "Giá (nghìn)": [wolf_buy_price / 1e3, wolf_sell_price / 1e3, wolf_diff_price / 1e3],
        "Khối lượng (nghìn)": [wolf_buy_volume / 1e3, wolf_sell_volume / 1e3, wolf_diff_volume / 1e3],
        "Giá trị (tỷ)": [wolf_buy_value / 1e9, wolf_sell_value / 1e9, wolf_diff_value / 1e9]
    }).set_index("Loại")
    rows[1].table(wolf_summary.style.format(precision=2, thousands=".", decimal=","))

    if len(wolf_buy):
        wolf_buy_hist = defaultdict(int)
        for i in wolf_buy.index:
            wolf_buy_hist[wolf_buy.price[i] / 1000] += wolf_buy.volume[i] / 1000
        wolf_buy_hist = pd.DataFrame(wolf_buy_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        wolf_buy_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="green", fontsize=18)
        rows[1].pyplot(fig)

    if len(wolf_sell):
        wolf_sell_hist = defaultdict(int)
        for i in wolf_sell.index:
            wolf_sell_hist[wolf_sell.price[i] / 1000] += wolf_sell.volume[i] / 1000
        wolf_sell_hist = pd.DataFrame(wolf_sell_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        wolf_sell_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="red", fontsize=18)
        rows[1].pyplot(fig)

    st.write("---")
    rows = st.columns(2)

    rows[0].write("Thống kê nhà đầu tư cáo (> 100 triệu)")
    fox_df = trading_df[trading_df["investor"] == InvestorType.FOX.value]

    fox_buy = fox_df[fox_df["match_type"] == "Buy"]
    fox_sell = fox_df[fox_df["match_type"] == "Sell"]

    fox_buy_volume = fox_buy["volume"].sum()
    fox_sell_volume = fox_sell["volume"].sum()
    fox_diff_volume = fox_buy_volume - fox_sell_volume

    fox_buy_value = fox_buy["value"].sum()
    fox_sell_value = fox_sell["value"].sum()
    fox_diff_value = fox_buy_value - fox_sell_value

    fox_buy_price = fox_buy_value / (fox_buy_volume + 1e-9)
    fox_sell_price = fox_sell_value / (fox_sell_volume + 1e-9)

    fox_diff_price = fox_diff_value / (fox_diff_volume + 1e-9)

    fox_summary = pd.DataFrame({
        "Loại": ["M", "B", "M-B"],
        "Giá (nghìn)": [fox_buy_price / 1e3, fox_sell_price / 1e3, fox_diff_price / 1e3],
        "Khối lượng (nghìn)": [fox_buy_volume / 1e3, fox_sell_volume / 1e3, fox_diff_volume / 1e3],
        "Giá trị (tỷ)": [fox_buy_value / 1e9, fox_sell_value / 1e9, fox_diff_value / 1e9]
    }).set_index("Loại")
    rows[0].table(fox_summary.style.format(precision=2, thousands=".", decimal=","))

    if len(fox_buy):
        fox_buy_hist = defaultdict(int)
        for i in fox_buy.index:
            fox_buy_hist[fox_buy.price[i] / 1000] += fox_buy.volume[i] / 1000
        fox_buy_hist = pd.DataFrame(fox_buy_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        fox_buy_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="green", fontsize=18)
        rows[0].pyplot(fig)

    if len(fox_sell):
        fox_sell_hist = defaultdict(int)
        for i in fox_sell.index:
            fox_sell_hist[fox_sell.price[i] / 1000] += fox_sell.volume[i] / 1000
        fox_sell_hist = pd.DataFrame(fox_sell_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        fox_sell_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="red", fontsize=18)
        rows[0].pyplot(fig)


    rows[1].write("Thống kê nhà đầu tư cừu (dưới 100 triệu)")
    sheep_df = trading_df[trading_df["investor"] == InvestorType.SHEEP.value]

    sheep_buy = sheep_df[sheep_df["match_type"] == "Buy"]
    sheep_sell = sheep_df[sheep_df["match_type"] == "Sell"]

    sheep_buy_volume = sheep_buy["volume"].sum()
    sheep_sell_volume = sheep_sell["volume"].sum()
    sheep_diff_volume = sheep_buy_volume - sheep_sell_volume

    sheep_buy_value = sheep_buy["value"].sum()
    sheep_sell_value = sheep_sell["value"].sum()
    sheep_diff_value = sheep_buy_value - sheep_sell_value

    sheep_buy_price = sheep_buy_value / (sheep_buy_volume + 1e-9)
    sheep_sell_price = sheep_sell_value / (sheep_sell_volume + 1e-9)

    sheep_diff_price = sheep_diff_value / (sheep_diff_volume + 1e-9)

    sheep_summary = pd.DataFrame({
        "Loại": ["M", "B", "M-B"],
        "Giá (nghìn)": [sheep_buy_price / 1e3, sheep_sell_price / 1e3, sheep_diff_price / 1e3],
        "Khối lượng (nghìn)": [sheep_buy_volume / 1e3, sheep_sell_volume / 1e3, sheep_diff_volume / 1e3],
        "Giá trị (tỷ)": [sheep_buy_value / 1e9, sheep_sell_value / 1e9, sheep_diff_value / 1e9]
    }).set_index("Loại")
    rows[1].table(sheep_summary.style.format(precision=2, thousands=".", decimal=","))

    if len(sheep_buy):
        sheep_buy_hist = defaultdict(int)
        for i in sheep_buy.index:
            sheep_buy_hist[sheep_buy.price[i] / 1000] += sheep_buy.volume[i] / 1000
        sheep_buy_hist = pd.DataFrame(sheep_buy_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        sheep_buy_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="green", fontsize=18)
        rows[1].pyplot(fig)

    if len(sheep_sell):
        sheep_sell_hist = defaultdict(int)
        for i in sheep_sell.index:
            sheep_sell_hist[sheep_sell.price[i] / 1000] += sheep_sell.volume[i] / 1000
        sheep_sell_hist = pd.DataFrame(sheep_sell_hist.items(), columns=["Giá (nghìn)", "Khối lượng (nghìn)"]).sort_values(by="Giá (nghìn)")
        fig, ax = plt.subplots(figsize=(10, 2))
        sheep_sell_hist.plot(kind="bar", x="Giá (nghìn)", y="Khối lượng (nghìn)", xlabel="", ylabel="", ax=ax, color="red", fontsize=18)
        rows[1].pyplot(fig)


    st.write("## Bảng giao dịch trong ngày")

    rows = st.columns(2)
    investors = list(InvestorType.__members__.keys())
    investor = rows[0].selectbox('Lọc nhà đầu tư:', investors, index=0)
    match_type = rows[1].selectbox('Lọc loại giao dịch:', ["Buy", "Sell", "ATO/ATC", "All"], index=3)


    filterd_df = trading_df[trading_df["investor"] == investor] if investor != InvestorType.ALL.value else trading_df
    filterd_df = filterd_df[filterd_df["match_type"] == match_type] if match_type != "All" else filterd_df
    filterd_df["time"] = filterd_df["time"].map(lambda x: x.strftime('%H:%M:%S'))

    # make unique datetime index
    filterd_df = filterd_df[::-1].reset_index(drop=True)
    
    rows = st.columns(6)
    rows[0].write("Số dòng: " + str(len(filterd_df)))
    filterd_df.columns = ["Thời gian", "Loại giao dịch", "Nhà đầu tư", "Giá", "Khối lượng", "Giá trị"]
    st.dataframe(filterd_df, width=1000, hide_index=True)
    