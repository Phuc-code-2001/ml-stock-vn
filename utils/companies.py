from streamlit import cache_data

from vnstock import listing_companies as _listing_companies

@cache_data
def listing_companies():
    return _listing_companies()

@cache_data
def listing_interested_companies():
    pass