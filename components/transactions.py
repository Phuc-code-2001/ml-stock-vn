import streamlit as st
import datetime as dt
import pandas as pd

from utils.transactions import get_transaction_today
from utils.enumtypes import InvestorType
from utils.formaters import hightlight_type, hightlight_investor
from utils.hooks import use_state

def render_transaction_today(symbol):

    trading_df = get_transaction_today(symbol)

    buy_df = trading_df[trading_df["match_type"] == "Buy"]
    sell_df = trading_df[trading_df["match_type"] == "Sell"]
    atc_df = trading_df[trading_df["match_type"] == "ATO/ATC"]

    buy_value = buy_df["value"].sum()
    sell_value = sell_df["value"].sum()

    buy_volume = buy_df["volume"].sum()
    sell_volume = sell_df["volume"].sum()

    total_volume = buy_volume + sell_volume
    total_value = buy_value + sell_value

    st.write(f"Thống kê giao dịch của mã {symbol} ngày {dt.datetime.today().strftime('%d/%m/%Y')}")
    st.write(f"Tổng cộng: {len(trading_df):,} giao dịch")
    st.write(f"Tổng khối lượng: {int(total_volume):,} đơn vị")
    st.write(f"Tổng giá trị: {total_value:,} VND")
    # put a horizontal line
    st.write('---')

    l1, r1 = st.columns(2)

    l1.write(f"Số lượng giao dịch mua: {len(buy_df):,}")
    l1.write(f"Tổng khối lượng mua: {buy_volume:,} đơn vị")
    l1.write(f"Tổng giá trị mua: {buy_value:,} VND")
        
    r1.write(f"Số lượng giao dịch bán: {len(sell_df):,}")
    r1.write(f"Tổng khối lượng bán: {sell_volume:,} đơn vị")
    r1.write(f"Tổng giá trị bán: {sell_value:,} VND")
        
    # put a horizontal line
    st.write("---")
    state_investor, set_state_investor = use_state("state_investor", InvestorType.ALL.value)
    
    trading_df.time = pd.to_datetime(trading_df.time, format='%H:%M:%S')
    filterd_df = trading_df
    filterd_df["time"] = filterd_df["time"].map(lambda x: x.strftime('%H:%M:%S'))
    filterd_df = (filterd_df[filterd_df["investor"] == state_investor()] if state_investor() != InvestorType.ALL.value else filterd_df)

    # make unique datetime index
    filterd_df = filterd_df[::-1].reset_index(drop=True)
    styled_df = filterd_df.style.apply(hightlight_type, subset=['match_type']) \
                                .apply(hightlight_investor, subset=['investor']) \
                                .format(precision=0, thousands=".", decimal=",")

    l2, r2 = st.columns(2)
    

    if state_investor() == InvestorType.ALL.value or state_investor() == InvestorType.SHARK.value:
        l2.write("Thống kê nhà đầu tư cá mập (> 1 tỷ)")
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
        l2.table(shark_summary.style.format(precision=2, thousands=".", decimal=","))

    if state_investor() == InvestorType.ALL.value or state_investor() == InvestorType.WOLF.value:
        r2.write("Thống kê nhà đầu tư sói (> 500 triệu)")
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
        r2.table(wolf_summary.style.format(precision=2, thousands=".", decimal=","))

    l3, r3 = st.columns(2)

    if state_investor() == InvestorType.ALL.value or state_investor() == InvestorType.FOX.value:

        l3.write("Thống kê nhà đầu tư cáo (> 100 triệu)")
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
        l3.table(fox_summary.style.format(precision=2, thousands=".", decimal=","))

    if state_investor() == InvestorType.ALL.value or state_investor() == InvestorType.SHEEP.value:

        r3.write("Thống kê nhà đầu tư cừu (dưới 100 triệu)")
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
        r3.table(sheep_summary.style.format(precision=2, thousands=".", decimal=","))

    investors = list(InvestorType.__members__.keys())
    investor = st.selectbox('Lọc nhà đầu tư:', investors, index=investors.index(state_investor()))
    set_state_investor(investor)
    rows = st.columns(7)
    rows[0].write("Số dòng: " + str(len(filterd_df)))
    st.table(styled_df)
    if rows[-1].button("Xác nhận", type='primary'):
        st.experimental_rerun()
