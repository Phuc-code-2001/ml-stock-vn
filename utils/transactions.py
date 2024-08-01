from vnstock3 import Vnstock
from .enumtypes import InvestorType
import pandas as pd
import os

from configs import INTRA_DATA_FOLDER

def get_investor_type(x):

    if x >= 1_000_000_000:
        return InvestorType.SHARK.value
    elif x >= 500_000_000:
        return InvestorType.WOLF.value
    elif x >= 100_000_000:
        return InvestorType.FOX.value
    
    return InvestorType.SHEEP.value

def get_transaction_today(symbol):
    vnstock = Vnstock(source="VCI").stock(symbol=symbol)
    df = vnstock.quote.intraday(symbol=symbol, page_size=15000)
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

def save_transactions(on_step_callback=None, on_complete_callback=None):
    save_symbols = [
        "FPT", "FTS", "FRT", "FOC", "FOX", 
        "CTR", "VTK", "VTP", 
        "MBB", "TCB", "VCB", "TPB", "BID",
        "MBS", "DSE", "VND", 
        "HVN",
    ]
    for i, symbol in enumerate(save_symbols):
        stock = Vnstock(source="VCI").stock(symbol=symbol)
        df = stock.quote.intraday(symbol, page_size=20000)
        date = df["time"].iloc[0].date().strftime(r"%Y-%m-%d")
        csv_path = os.path.join(INTRA_DATA_FOLDER, symbol, f"{date}.csv")
        df.to_csv(csv_path, index=False)
        if on_step_callback:
            on_step_callback(i, symbol)
    
    if on_complete_callback:
        on_complete_callback()