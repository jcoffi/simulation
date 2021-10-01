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
    dly_return = daily_return(etf_prices, remove_first_date=True, in_percent=True)
    # since daily libor is missing some days, remove those days from dly_return & lev_return
    dly_return = dly_return[dly_return.index.isin(daily_libor.index)]
    lev_return = dly_return * leverage

    lev_etf = lev_return - expense_ratio/250 - (leverage - 1) * daily_libor * 1 / 360
    # since some etf_prices skip a lot of data in the 1980s (but LIBOR is fully logged), remove all NAN
    lev_etf = lev_etf.dropna()

    dly_return['Cumulative'] = 100.0
    idx = -1
    for _, row in dly_return.iterrows():
        idx += 1
        if idx == 0:
            continue

        print(dly_return['Cumulative'].iloc[idx-1], row['Value'])
        row['Cumulative'] = dly_return['Cumulative'].iloc[idx-1] * row['Value']

    print(dly_return)

    # if normalize_to_one:
    #     tvalue = 13.89
    #     f_diff = tvalue - lev_etf['Value'].iloc[0]
    #     f_diff = 0
    # lev_etf /= abs(lev_etf['Value'].iloc[0])  # normalize by the value of the inception date
    return lev_etf

if __name__ == '__main__':
    libor_inception_date = datetime(1986, 1, 2)
    libor_inception_prev_date = libor_inception_date - timedelta(days=2)  # Jan 1 is market holiday, so get 1985-12-31
    last_data_date = '2021-09-01'  # get until Sep 1, 2021
    # first_data_date = '1986-01-02'
    # first_data_date = '2009-01-01'
    first_data_date = '2009-06-03'
    sp500_inception_date = datetime(1984, 12, 1)
    upro_inception_date = datetime(2009, 6, 3)

    #
    # Gets and Process LIBOR
    #
    df_libor = pd.read_csv('../dataset/USD1MTD156N.csv', index_col='DATE')
    df_libor = df_libor[df_libor.USD1MTD156N != '.'].loc[:last_data_date]
    df_libor.USD1MTD156N = pd.to_numeric(df_libor.USD1MTD156N)
    df_libor.index = pd.to_datetime(df_libor.index)
    df_libor = df_libor.rename(columns={'USD1MTD156N': 'Value'})

    #
    # S&P 500 -- index UPRO follows
    # TMF - Index the ICE (started 2004)
    #
    sp500 = web.DataReader('^GSPC', 'yahoo', sp500_inception_date, datetime(2021, 9, 1))['Adj Close']
    df_sp500 = pd.DataFrame(data={'Value': sp500})[first_data_date:]

    #
    # Actual UPRO data from 2009
    #
    upro_actual = web.DataReader('UPRO', 'yahoo', sp500_inception_date, datetime(2021, 9, 1))['Adj Close']

    # qqq_returns = daily_leveraged_etf(df_ndqcom, daily_libor=df_libor, leverage=1, expense_ratio=0.2)
    # qqq = qqq_returns.cumsum()
    # Er is 1.06%
    upro_returns = daily_leveraged_etf(df_sp500, daily_libor=df_libor, leverage=1, expense_ratio=0.93, in_percent=False)
    upro = upro_returns.cumsum()
    print(upro)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))

    # Plot TMF and drawdown
    ax1.title.set_text('UPRO Simulated')
    ax1.plot(upro, label='UPRO (Sim)')
    # ax1.set_yscale('log')
    # ax1.plot(df_xiusa000ml, label='Barclays Capital U.S. 20+ Year Treasury Bond Index')
    upro_actual.plot(ax=ax1, label='UPRO (Real)')
    ax1.legend()

    # drawdown_tmf = drawdown(tmf_returns)
    # ax2.title.set_text('Drawdown of TMF Simulated')
    # drawdown_tmf.plot.area(ax=ax2, label='TMF (Sim)', color='red')

    # print(f"TMF Sim Drawdown: {drawdown_tmf.idxmin()} {drawdown_tmf.min():.2f}%")

    plt.show()

