from streamlit import cache_data, cache_resource
import datetime as dt

from .connections import get_collection

daily_transactions = get_collection("stock_db", "daily_transactions")
utils = get_collection("stock_db", "utils")

@cache_data
def get_interested_symbols():
    query = {"key": "interested_symbols"}
    document = utils.find_one(query)
    return document["value"]

@cache_data
def get_daily_transactions(symbol: str, date: dt.date):
    begin_of_day = dt.datetime(year=date.year, month=date.month, day=date.day, hour=9, minute=0, second=0)
    end_of_day = begin_of_day.replace(hour=15, minute=0, second=0)
    query = { "symbol": symbol, "__datetime__": {"$gte": begin_of_day, "$lte": end_of_day} }
    return list(daily_transactions.find(query).sort("__datetime__", -1).limit(20000))