from streamlit import cache_data
import datetime as dt

from .connections import get_collection
from utils.transactions import get_infraday_data

daily_transactions = get_collection("stock_db")
utils = get_collection("stock_db", "utils")

@cache_data
def get_interested_symbols():
    query = {"key": "interested_symbols"}
    document = utils.find_one(query)
    return document["value"]

def get_daily_transactions(symbol: str, date: dt.date):
    begin_of_day = dt.datetime(year=date.year, month=date.month, day=date.day, hour=9, minute=0, second=0)
    end_of_day = begin_of_day.replace(hour=15, minute=0, second=0)
    query = { "symbol": symbol, "__datetime__": {"$gte": begin_of_day, "$lte": end_of_day} }
    return list(daily_transactions.find(query).sort("__datetime__", -1).limit(20000))

def update_and_save_recent_transactions(on_step_callback=lambda x: 0, on_complete_callback=lambda x: 0):
    
    symbols = get_interested_symbols()
    for i, symbol in enumerate(symbols):
        df = get_infraday_data(symbol)
        df['symbol'] = symbol
        df['id'] = df['id'].map(int)
        df['time'] = df['time'].map(str)
        df['__datetime__'] = df['time'].map(lambda x: dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
        documents = df.to_dict("records")
        insert_documents = []
        for j, document in enumerate(documents):
            if daily_transactions.find_one({"id": document["id"]}) is None:
                insert_documents.append(document)
            step_ratio = ((i + 1) / len(symbols)) - (1 - ((j + 1) / len(documents))) * (1 / len(symbols))
            on_step_callback(step_ratio)
        
        if insert_documents:
            print("Inserting", len(insert_documents), "documents of symbol", symbol)
            daily_transactions.insert_many(insert_documents)
            print("Complete inserted", len(insert_documents), "documents.")

    collection_count = daily_transactions.estimated_document_count()
    on_complete_callback(collection_count)