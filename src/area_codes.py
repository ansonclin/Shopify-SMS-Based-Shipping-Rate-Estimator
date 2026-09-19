#2
import pandas as pd

def extract_area_code(phone_number):
    area_code = phone_number[1:4]
    return area_code

def add_area_code_column(df):
    df["area_code"] = df["phone_number"].apply(extract_area_code) # creates a brand new column and stores area code only
    return df 

