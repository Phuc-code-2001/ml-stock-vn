from vnstock3 import Vnstock
from .enumtypes import InvestorType
import pandas as pd
import os

from configs import INTRA_DATA_FOLDER

def get_investor_type(x):
    if x >= 5_000_000_000:
        return InvestorType.SHARK.value
    elif x >= 1_000_000_000:
        return InvestorType.WOLF.value
    elif x >= 100_000_000:
        return InvestorType.FOX.value
    
    return InvestorType.SHEEP.value

def get_infraday_data(symbol, page_size=20000):
    vnstock = Vnstock(source="VCI").stock(symbol=symbol)
    return vnstock.quote.intraday(symbol=symbol, page_size=page_size)

def get_transaction_today(symbol):
    df = get_infraday_data(symbol)
    df["value"] = df["price"] * df["volume"]
    df["investor"] = df["value"].apply(get_investor_type)
    df.loc[df["match_type"] == "ATO/ATC", ["investor"]] = "ATO/ATC"
    return df[["time", "match_type", "investor", "price", "volume", "value"]]

def get_transaction_on_date(symbol, date):

    csv_path = os.path.join(INTRA_DATA_FOLDER, symbol, f"{date}.csv")
    df = pd.read_csv(csv_path)
    df["value"] = df["price"] * df["volume"]
    df["investor"] = df["value"].apply(get_investor_type)
    df.loc[df["match_type"] == "ATO/ATC", ["investor"]] = "ATO/ATC"
    return df[["time", "match_type", "investor", "price", "volume", "value"]]