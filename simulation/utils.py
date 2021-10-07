from datetime import datetime

import pandas as pd


def total_return(prices):
    """ Calulates the growth of 1 dollar invested in a stock with given prices """
    return (1 + prices.pct_change(1)).cumprod()


def drawdown(prices):
    """ Calulates the drawdown of a stock with given prices """
    rets = total_return(prices)
    return (rets.div(rets.cummax()) - 1) * 100


def daily_return(prices, remove_first_date=False):
    """ Daily return """
    # returns = prices.pct_change(1) if in_percent else prices.diff(1)
    returns = prices.pct_change(1)
    return returns[1:] if remove_first_date else returns


def compound_return(etf: pd.DataFrame, starting_amount: float = 1.0, base_col: str = 'Close') -> pd.DataFrame:
    total_val = starting_amount
    df = pd.DataFrame(index=etf.index)
    df.loc[df.iloc[0], 'Investment'] = total_val

    row_idx = 0
    for index, _ in df.iterrows():
        if row_idx != 0:
            total_val = total_val + total_val * etf.loc[index, base_col]

        # df.at[index, 'Investment'] = total_val
        df.loc[index, 'Investment'] = total_val
        row_idx += 1

    return df


def process_libor(csv_path: str) -> pd.Series:
    """
    Gets and Process LIBOR
    :param csv_path: Path to CSV
    # :param last_data_date: End date for LIBOR data
    :return:
    """
    df_libor = pd.read_csv(csv_path, index_col='DATE')
    df_libor = df_libor[df_libor['USD1MTD156N'] != '.'] # .loc[:last_data_date]
    df_libor['USD1MTD156N'] = pd.to_numeric(df_libor['USD1MTD156N'])
    df_libor.index = pd.to_datetime(df_libor.index)
    df_libor = df_libor.rename(columns={'USD1MTD156N': 'LIBOR'})

    # READ: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
    # freq='B' for Business Offset
    # column `Value`: (1 month LIBOR) * (Current date - previous date)/360
    d_shifted = df_libor.index.shift(-1, freq='B')
    df_libor_day_delta = pd.to_datetime(df_libor.index) - pd.to_datetime(d_shifted)
    df_libor['Value'] = pd.concat([df_libor['LIBOR'] * abs(df_libor_day_delta.days)], axis=1)

    return df_libor
