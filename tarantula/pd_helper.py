import pandas as pd

def print_df(df):
    """Print a whole series regardless of how big it is"""
    with pd.option_context('display.max_rows', len(df),
                           'display.max_columns', len(df.columns)):
        print(df)
