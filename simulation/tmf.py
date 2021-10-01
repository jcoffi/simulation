from datetime import datetime, timedelta

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt


def total_return(prices):
    """ Calulates the growth of 1 dollar invested in a stock with given prices """
    return (1 + prices.pct_change(1)).cumprod()


def drawdown(prices):
    """
    Calulates the drawdown of a stock with given prices
    """
    rets = total_return(prices)
    return (rets.div(rets.cummax()) - 1) * 100


def daily_return(prices, remove_first_date=False, in_percent=False):
    """ Daily return """
    returns = prices.pct_change(1) if in_percent else prices.diff(1)
    return returns[1:] if remove_first_date else returns


def daily_leveraged_etf(etf_prices, daily_libor, leverage=1, expense_ratio=0.2, in_percent=False, normalize_to_one=True):
    """
    https://www.bogleheads.org/forum/viewtopic.php?f=10&t=272007
    Daily performance of a leveraged ETF is:
    (Daily % of underlying total return index) * X - ER/250 - (X - 1) * (1 month LIBOR) * (Current date - previous date)/360
    where X is the leverage (e.g. 2 or 3), the current date is the current date and the previous date is the previous trading day.

    normalize_to_one: If true, set the inception date's value as 1 (should be kept True)
    """
    print(etf_prices)
    dly_return = daily_return(etf_prices, remove_first_date=True, in_percent=in_percent)
    # since daily libor is missing some days, remove those days from dly_return & lev_return
    dly_return = dly_return[dly_return.index.isin(daily_libor.index)]
    lev_return = dly_return * leverage

    lev_etf = lev_return - expense_ratio/250 - (leverage - 1) * daily_libor * 1 / 360
    # since some etf_prices skip a lot of data in the 1980s (but LIBOR is fully logged), remove all NAN
    lev_etf = lev_etf.dropna()
    print(lev_etf)
    if normalize_to_one:
        tvalue = 13.89
        f_diff = tvalue - lev_etf['Value'].iloc[0]
        f_diff = 0
        lev_etf = (lev_etf + f_diff) / abs(lev_etf['Value'].iloc[0])  # normalize by the value of the inception date
    return lev_etf

if __name__ == '__main__':
    libor_inception_date = datetime(1986, 1, 2)
    libor_inception_prev_date = libor_inception_date - timedelta(days=2)  # Jan 1 is market holiday, so get 1985-12-31
    last_data_date = '2021-09-01'  # get until Sep 1, 2021
    # first_data_date = '1986-01-02'
    # first_data_date = '2009-01-01'
    first_data_date = '2009-04-16'
    tmf_inception_date = datetime(2009, 4, 16)

    #
    # Gets and Process LIBOR
    #
    df_libor = pd.read_csv('../dataset/USD1MTD156N.csv', index_col='DATE')
    df_libor = df_libor[df_libor.USD1MTD156N != '.'].loc[:last_data_date]
    df_libor.USD1MTD156N = pd.to_numeric(df_libor.USD1MTD156N)
    df_libor.index = pd.to_datetime(df_libor.index)
    df_libor = df_libor.rename(columns={'USD1MTD156N': 'Value'})

    #
    # XIUSA000ML.csv -- The index TMF used to follow
    # TMF - Index the ICE (started 2004)
    #
    df_xiusa000ml = pd.read_csv('../dataset/XIUSA000ML.csv', index_col='Date')
    # print(df_xiusa000ml)
    df_xiusa000ml = df_xiusa000ml.loc[first_data_date:last_data_date]
    df_xiusa000ml.index = pd.to_datetime(df_xiusa000ml.index)

    #
    # Actual TMF data from 2009
    #
    tmf_actual = web.DataReader('TMF', 'yahoo', tmf_inception_date, datetime(2021, 9, 1))['Adj Close']

    # qqq_returns = daily_leveraged_etf(df_ndqcom, daily_libor=df_libor, leverage=1, expense_ratio=0.2)
    # qqq = qqq_returns.cumsum()
    # Er is 1.06%
    tmf_returns = daily_leveraged_etf(df_xiusa000ml, daily_libor=df_libor, leverage=3, expense_ratio=1.06, in_percent=False)
    tmf = tmf_returns.cumsum()
    print(tmf)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))

    # Plot TMF and drawdown
    ax1.title.set_text('TMF Simulated')
    ax1.plot(tmf, label='TMF (Sim)')
    # ax1.set_yscale('log')
    # ax1.plot(df_xiusa000ml, label='Barclays Capital U.S. 20+ Year Treasury Bond Index')
    tmf_actual.plot(ax=ax1, label='TMF (Real)')
    ax1.legend()

    # drawdown_tmf = drawdown(tmf_returns)
    # ax2.title.set_text('Drawdown of TMF Simulated')
    # drawdown_tmf.plot.area(ax=ax2, label='TMF (Sim)', color='red')

    # print(f"TMF Sim Drawdown: {drawdown_tmf.idxmin()} {drawdown_tmf.min():.2f}%")

    plt.show()

