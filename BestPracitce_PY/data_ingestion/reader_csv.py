import pandas as pd
def load_csv(filepath):
    return pd.read_csv(filepath, encoding='utf-8', sep=';', on_bad_lines='skip')
