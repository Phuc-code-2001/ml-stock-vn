import numpy as np

def hightlight_type(type_columns, sell="color:white;background-color:purple;", buy="color:white;background-color:green"):
    return np.where(type_columns == "Sell", sell, buy)

def hightlight_investor(
        investor_columns, 
        shark="color:red;background-color:lightblue", 
        wolf="color:white;background-color:lightgray", 
        fox="color:black;background-color:lightgreen",
        sheep="color:white;background-color:darksalmon"):
    return np.where(investor_columns == "SHARK", shark, np.where(investor_columns == "WOLF", wolf, np.where(investor_columns == "FOX", fox, sheep)))