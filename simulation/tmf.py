from datetime import datetime, timedelta

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

from utils import daily_return, process_libor


AVG_TRADING_DAYS_PER_YEAR = 252


def daily_leveraged_etf(etf_prices, daily_libor, starting_amount=1, leverage=1, expense_ratio=0.2):
    """
    https://www.bogleheads.org/forum/viewtopic.php?f=10&t=272007
    Daily performance of a leveraged ETF (in percentage) is:
    (Daily % of underlying total return index) * X - ER/250 - (X - 1) * (1 month LIBOR) * (Current date - previous date)/360
    where X is the leverage (e.g. 2 or 3), the current date is the current date and the previous date is the previous trading day.

    daily_libor: passed as percentage (0 to 100)
    expense_ratio: passed as percentage (0 to 100)
    """

    # convert all passed percentage parameters to decimal 0 - 1
    expense_ratio = expense_ratio / 100
    daily_libor = daily_libor / 100

    dly_return = daily_return(etf_prices, remove_first_date=True)
    # since daily libor is missing some days, remove those days from dly_return & lev_return
    dly_return = dly_return[dly_return.index.isin(daily_libor.index)]
    lev_return = dly_return * leverage

    etf_expense = expense_ratio / AVG_TRADING_DAYS_PER_YEAR
    # leverage_expense = (leverage - 1) * daily_libor * 1 / 360
    leverage_expense = (leverage - 1) * daily_libor * 1 / 252

    lev_etf = lev_return - etf_expense # subtract etf_expense
    lev_etf = lev_etf.subtract(leverage_expense, axis=0)  # subtract lev_expense on index
    # since some etf_prices skip a lot of data in the 1980s (but LIBOR is fully logged), remove all NaN
    lev_etf = lev_etf.dropna()

    #
    # TODO: Account for trading fee & slippage
    #

    # Compound gain/loss with starting amount
    total_val = starting_amount
    lev_etf.iloc[0]['Investment'] = total_val
    row_idx = 0
    for index, row in lev_etf.iterrows():
        if row_idx != 0:
            total_val = total_val + total_val * row['Close']

        lev_etf.at[index, 'Investment'] = total_val
        row_idx += 1

    return lev_etf

if __name__ == '__main__':
    libor_inception_date = datetime(1986, 1, 2)
    libor_inception_prev_date = libor_inception_date - timedelta(days=2)  # Jan 1 is market holiday, so get 1985-12-31
    last_data_date = datetime(2021, 9, 1)  # get until Sep 1, 2021
    # first_data_date = datetime(1986, 1, 2)
    # first_data_date = datetime(1992, 1, 2)
    first_data_date = datetime(2009, 4, 16)
    tmf_inception_date = datetime(2009, 4, 16)

    df_libor = process_libor('../dataset/USD1MTD156N.csv')

    #
    # XIUSA000ML.csv -- The index TMF used to follow
    # Index name: Bloomberg Barclays US Government Long TR USD
    # Data: http://quotes.morningstar.com/indexquote/quote.html?t=XIUSA000ML
    # Info: The Bloomberg US Treasury: Long Index measures US dollar-denominated, fixed-rate,
    #       nominal debt issued by the US Treasury with 10 years or more to maturity.
    # From Bloomberg: https://www.bloomberg.com/quote/LUTLTRUU:IND
    # Misc.: https://www.bloomberg.com/quote/LUAGTRUU:IND
    # TMF - Index the ICE (started 2004)
    #
    df_xiusa000ml = pd.read_csv('../dataset/XIUSA000ML.csv', index_col='Date')
    df_xiusa000ml = df_xiusa000ml.loc[first_data_date.strftime('%Y-%m-%d'):last_data_date.strftime('%Y-%m-%d')]
    df_xiusa000ml.index = pd.to_datetime(df_xiusa000ml.index)

    #
    # Actual TMF data from 2009
    #
    tmf_actual = web.DataReader('TMF', 'yahoo', tmf_inception_date, last_data_date)['Adj Close']

    #
    # Simulate TMF (ER is 1.06%)
    #
    tmf_returns = daily_leveraged_etf(df_xiusa000ml, daily_libor=df_libor['Value'], leverage=3, expense_ratio=1.06, starting_amount=11.15)

    print(tmf_returns)

    # Plot TMF
    plt.plot(tmf_returns.index, tmf_returns['Investment'], label='TMF (Sim)')
    ax = plt.gca()

    tmf_actual.plot(ax=ax, label='TMF (Real)')
    ax.legend()

    plt.show()


