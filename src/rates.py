#5
import pandas as pd
from dotenv import load_dotenv
import os
import requests

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

    rate_for_area_code = None
    for rate in shipment["rates"]:
        if rate["carrier"] == "USPS" and rate["service"] == "GroundAdvantage":
            rate_for_area_code = float(rate["rate"])

    return rate_for_area_code