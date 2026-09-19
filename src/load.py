#1
import pandas as pd

def load_signups(csv_path):
    df = pd.read_csv(csv_path, dtype={"phone_number": str})
    return df 