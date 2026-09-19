#5
import pandas as pd
from dotenv import load_dotenv
import os 
import requests 
from load import load_signups
from area_codes import add_area_code_column

df = load_signups("SMS_Subscribers.csv")
df = add_area_code_column(df)


load_dotenv()
api_key = os.getenv("EASYPOST_API_KEY")


reference_df = pd.read_csv("data/area_code_reference.csv", dtype = {"area_code": str, "representative_zip": str})

def get_zip_for_area_code(area_code):
    match = reference_df[reference_df["area_code"] == area_code]
    return match["representative_zip"].iloc[0]

def get_rate_for_area_code(area_code):

    destination_zip = get_zip_for_area_code(area_code)

    response = requests.post(
    "https://api.easypost.com/v2/shipments",
    auth=(api_key, ""),
    json = {
        "shipment":{
            "to_address": {"zip": destination_zip, "country": "US"},
            "from_address": {"zip": "94122", "country": "US"},
            "parcel": {"weight": 32, "length": 16, "width": 14.5, "height": 2}
        }
    })

    shipment = response.json()

    for rate in shipment["rates"]:
        if rate["carrier"] == "USPS" and rate["service"] == "GroundAdvantage":
            ground_advantage_rate = float(rate["rate"])

    return ground_advantage_rate

print(get_rate_for_area_code("910"))

rate_cache = {}
for area_code in df["area_code"].unique()[:3]:
    rate_cache[area_code] = get_rate_for_area_code(area_code)

print(rate_cache)