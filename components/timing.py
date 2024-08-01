import datetime as dt
import streamlit as st
import threading

def update_time(progress, on_get_time_callback, widget=st):
    while True:
        time = on_get_time_callback()
        ratio = (time.hour * 3600 + time.minute * 60 + time.second) / (24 * 3600)
        progress.progress(ratio, f"Thời gian máy chủ: {time.strftime(r'%H:%M:%S')}")
        progress.refresh()
        widget.sleep(1)

def render_time(on_get_time_callback: dt.datetime, widget=st):
    _time = on_get_time_callback()
    _time_ratio = (_time.hour * 3600 + _time.minute * 60 + _time.second) / (24 * 3600)
    _time_progress = widget.progress(_time_ratio, f"Thời gian máy chủ: {_time.strftime(r'%H:%M:%S')}")

    thread = threading.Thread(target=update_time, args=(_time_progress, on_get_time_callback))
    thread.start()