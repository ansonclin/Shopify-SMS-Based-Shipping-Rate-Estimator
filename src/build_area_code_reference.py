#4
import pandas as pd

df = pd.read_csv("data/raw/npa_zip_data.csv" , dtype ={"zipCode": str}) # load 427k file
grouped = df.groupby("npa").first() # collapse to one row per unique area code, groupby("npa") to group area codes 
grouped = grouped.reset_index() # fixes index to numbers so "npa" is no longer counted as an index
 
reference_table = grouped[["npa", "zipCode", "city", "state", "country"]].rename(columns = {"npa": "area_code", "zipCode": "representative_zip", "state": "region"}) 

print(reference_table.head())

reference_table.to_csv("data/area_code_reference.csv",index = False) # creates a csv under data 