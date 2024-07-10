import pandas as pd
import numpy as np
from vietnam_number import n2w

def hightlight_type(type_columns, sell="color:white;background-color:purple;", buy="color:white;background-color:green"):
    return np.where(type_columns == "SELL", sell, buy)

def hightlight_investor(investor_columns, shark="color:red;background-color:lightblue", wolf="color:white;background-color:lightgray", sheep="color:black;background-color:lightgreen"):
    return np.where(investor_columns == "SHARK", shark, np.where(investor_columns == "WOLF", wolf, sheep))

def vi_number_format(number):
    number = str(int(number))
    return n2w(number)