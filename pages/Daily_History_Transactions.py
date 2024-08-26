import streamlit as st
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from licenses import accept_licence
accept_licence()

from databases.functions import get_daily_transactions, get_interested_symbols, update_and_save_recent_transactions
from components.sidebar import render_sidebar

from utils.timing import get_recent_trading_day, get_current_datetime
from databases.managers import manager_dict, ProgressManager

render_sidebar(st)

selected_symbol = st.selectbox("Chọn mã cổ phiếu", get_interested_symbols(), index=None, key="selected_symbol")
selected_date = st.date_input("Chọn ngày", dt.datetime.now(), min_value=None, max_value=None, key="selected_date")

if selected_symbol:
    transactions = get_daily_transactions(selected_symbol, selected_date)
    if not transactions:
        st.write(f"Không có thông tin giao dịch cho {selected_symbol} ngày {selected_date}")
        recent_trading_date = get_recent_trading_day()
        print("recent_trading_date:", recent_trading_date)
        now_datetime = get_current_datetime()
        print("now_datetime:", now_datetime)
        if recent_trading_date.date() == selected_date and (now_datetime.hour <= 5 or now_datetime.hour >= 15 or now_datetime.weekday() in [5, 6]):
            if st.button(f"Cập nhật dữ liệu {recent_trading_date.date()}", key="update"):
                progress_bar = st.progress(0, text="Đang cập nhật dữ liệu...")
                progress_manager = manager_dict.get("progress_manager")
                if progress_manager is None or progress_manager.is_completed:
                    on_step_callback = lambda x: progress_bar.progress(x, text=f"Đang cập nhật dữ liệu {x * 100:.2f}%")
                    on_complete_callback = lambda x: progress_bar.text("Cập nhật dữ liệu thành công!")
                    progress_manager = ProgressManager(update_and_save_recent_transactions, on_step_callback, on_complete_callback)
                    manager_dict["progress_manager"] = progress_manager
                    progress_manager.start()
                else:
                    progress_manager.wait_until_complete()
                
    else:
        df = pd.DataFrame(transactions, columns=["time", "price", "volume", "match_type"])
        df.convert_dtypes()
        df["value"] = df["price"] * df["volume"]
        avg_price = df["price"].mean()
        total_volume = df["volume"].sum()
        total_value = df["value"].sum()
        rows = st.columns(2)
        rows[0].write(f"**Các thông tin cơ bản:**")
        rows[0].write(f"Giá giao dịch trung bình: {avg_price:,.0f} (VND)")
        rows[0].write(f"Tổng khối lượng giao dịch: {total_volume:,.0f} (đơn vị)")
        rows[0].write(f"Tổng giá trị giao dịch: {total_value:,.0f} (VND)")
        min_price = df["price"].min()
        min_price_volume = df[df["price"] == min_price]["volume"].sum()
        max_price = df["price"].max()
        max_price_volume = df[df["price"] == max_price]["volume"].sum()
        ato_atc_df = df[df["match_type"] == "ATO/ATC"]
        open_price = ato_atc_df["price"].iloc[-1]
        open_volume = ato_atc_df["volume"].iloc[-1]
        close_price = ato_atc_df["price"].iloc[0]
        close_volume = ato_atc_df["volume"].iloc[0]
        rows[1].write(f"**Các thông tin khác:**")
        rows[1].html(
            f"""
            <div style='color: green'>Giá mở cửa: {open_price:,.0f}</div>
            <div style='color: green'>Khối lượng: {open_volume:,.0f}</div>
            <hr style='margin-block: 8px'></hr>
            <div style='color: blue'>Giá thấp nhất: {min_price:,.0f}</div>
            <div style='color: blue'>Khối lượng: {min_price_volume:,.0f}</div>
            <hr style='margin-block: 8px'></hr>
            <div style='color: purple'>Giá cao nhất: {max_price:,.0f}</div>
            <div style='color: purple'>Khối lượng: {max_price_volume:,.0f}</div>
            <hr style='margin-block: 8px'></hr>
            <div style='color: red'>Giá đóng cửa: {close_price:,.0f}</div>
            <div style='color: red'>Khối lượng: {close_volume:,.0f}</div>
            """
        )

        st.write(f"**Phân phối mua bán:**")
        sell_df = df[df["match_type"] == "Sell"]
        buy_df = df[df["match_type"] == "Buy"]
        rows = st.columns(3)
        sell_group = sell_df[["price", "volume"]].groupby("price").sum()["volume"].map(lambda x: x / 1000).sort_index()
        sell_group.index = sell_group.index / 1000
        fig, ax = plt.subplots(figsize=(4, 8))
        sell_group.plot(kind="barh", ax=ax, color="blue", label="KL Bán (Nghìn)", legend=True, ylabel="", xlabel="")
        rows[0].pyplot(fig)

        buy_group = buy_df[["price", "volume"]].groupby("price").sum()["volume"].map(lambda x: x / 1000).sort_index()
        buy_group.index = buy_group.index / 1000
        fig, ax = plt.subplots(figsize=(4, 8))
        buy_group.plot(kind="barh", ax=ax, color="green", label="KL Mua (Nghìn)", legend=True, ylabel="", xlabel="")
        rows[1].pyplot(fig)

        merged = pd.merge(sell_group, buy_group, left_index=True, right_index=True, how="outer").fillna(0)[["volume_x", "volume_y"]]
        merged.rename(columns={"volume_x": "KL Bán (Nghìn)", "volume_y": "KL Mua (Nghìn)"}, inplace=True)
        fig, ax = plt.subplots(figsize=(4, 8))
        merged.plot(kind="barh", ax=ax, color=["blue", "green"], ylabel="", xlabel="", stacked=True)
        rows[2].pyplot(fig)

        st.write(f"## Bảng giao dịch:")
        expander = st.expander("Bộ lọc")
        filtered_match_type = expander.selectbox("Loại giao dịch: ", ["Tất cả"] + df["match_type"].unique().tolist(), index=0, key="filtered_match_type")
        
        filtered_type_df = df if filtered_match_type == "Tất cả" else df[df["match_type"] == filtered_match_type]

        filtered_scale_type = expander.radio("Lọc theo độ lớn: ", options=["Giá", "Khối Lượng", "Giá trị giao dịch"], index=1,  horizontal=True)

        if filtered_scale_type == "Khối Lượng":
            filtered_volume_options = filtered_type_df["volume"].sort_values().unique().tolist()
            filtered_volume = expander.selectbox(
                "Khối lượng giao dịch từ: ",
                options=filtered_volume_options,
                index=0
            )
            filtered_volume_df = filtered_type_df[filtered_type_df["volume"] >= filtered_volume]
            df = filtered_volume_df
        elif filtered_scale_type == "Giá":
            filtered_price_options = filtered_type_df["price"].sort_values().unique().tolist()
            filtered_price = expander.selectbox(
                "Giá giao dịch từ: ",
                options=filtered_price_options,
                index=0
            )
            filtered_price_df = filtered_type_df[filtered_type_df["price"] >= filtered_price]
            df = filtered_price_df
        elif filtered_scale_type == "Giá trị giao dịch":
            filtered_value_options = filtered_type_df["value"].sort_values().map(lambda x: round(x / 1000000)).unique().tolist()
            filtered_value = expander.selectbox(
                "Giá trị giao dịch từ (triệu đồng): ",
                options=filtered_value_options,
                format_func=lambda x: f"{x:,.0f}",
                index=0
            )
            filtered_value_df = filtered_type_df[filtered_type_df["value"] >= filtered_value * 1000000]
            df = filtered_value_df

        df["time"] = df["time"].map(lambda x: str(x).split()[-1])
        df.columns = ["Thời gian", "Giá", "Khối lượng", "Loại giao dịch", "Giá trị"]
        st.dataframe(df, hide_index=True, width=1000, height=None)