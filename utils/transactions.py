from vnstock3 import Vnstock
from .enumtypes import InvestorType

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
    df = vnstock.quote.intraday(symbol=symbol, page_size=10000)
    df["value"] = df["price"] * df["volume"]
    df["investor"] = df["value"].apply(get_investor_type)
    return df[["time", "match_type", "investor", "price", "volume", "value"]]