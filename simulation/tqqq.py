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


def daily_leveraged_etf(etf_prices, daily_libor, leverage=1, expense_ratio=0.2, in_percent=False):
    """
    https://www.bogleheads.org/forum/viewtopic.php?f=10&t=272007
    Daily performance of a leveraged ETF is:
    (Daily % of underlying total return index) * X - ER/250 - (X - 1) * (1 month LIBOR) * (Current date - previous date)/360
    where X is the leverage (e.g. 2 or 3), the current date is the current date and the previous date is the previous trading day.
    """
    dly_return = daily_return(etf_prices, remove_first_date=True, in_percent=in_percent)
    # since daily libor is missing some days, remove those days from dly_return & lev_return
    dly_return = dly_return[dly_return.index.isin(daily_libor.index)]
    lev_return = dly_return * leverage

    lev_etf = lev_return - expense_ratio/250 - (leverage - 1) * daily_libor * 1 / 360
    return lev_etf.dropna()


if __name__ == '__main__':
    libor_inception_date = datetime(1986, 1, 2)
    libor_inception_date = datetime(1995, 1, 2)
    libor_inception_prev_date = libor_inception_date - timedelta(days=2)  # Jan 1 is market holiday, so get 1985-12-31

    df_libor = pd.read_csv('../dataset/USD1MTD156N.csv', index_col='DATE')
    df_libor = df_libor[df_libor.USD1MTD156N != '.'].loc[:'2021-09-01']  # get until Sep 1, 2021
    df_libor.USD1MTD156N = pd.to_numeric(df_libor.USD1MTD156N)
    df_libor.index = pd.to_datetime(df_libor.index)
    df_libor = df_libor.rename(columns={'USD1MTD156N': 'Value'})

    #
    # Nasdaq Composite
    #
    ndqcom = web.DataReader('^IXIC', 'yahoo', libor_inception_prev_date, datetime(2021, 9, 1))['Adj Close']  # get until Sep 1, 2021
    df_ndqcom = pd.DataFrame(data={'Value': ndqcom})

    #
    # TQQQ Actual Data
    #
    tqqq_actual = web.DataReader('TQQQ', 'yahoo', libor_inception_prev_date, datetime(2021, 9, 1))['Adj Close']  # get until Sep 1, 2021

    # qqq_returns = daily_leveraged_etf(df_ndqcom, daily_libor=df_libor, leverage=1, expense_ratio=0.2)
    # qqq = qqq_returns.cumsum()
    tqqq_returns = daily_leveraged_etf(df_ndqcom, daily_libor=df_libor, leverage=3, expense_ratio=0.95)
    tqqq = tqqq_returns.cumsum()
    print(tqqq)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))

    # Plot TQQQ and drawdown
    ax1.title.set_text('TQQQ Simulated')
    ax1.plot(tqqq, label='TQQQ (Sim)')
    ax1.set_yscale('log')
    ax1.plot(ndqcom, label='Nasdaq Composite')
    ax1.legend()

    tqqq_actual.plot(ax=ax1, label='TQQQ (Actual)')

    drawdown_tqqq = drawdown(tqqq)
    ax2.title.set_text('Drawdown of TQQQ Simulated')
    drawdown_tqqq.plot.area(ax=ax2, label='TQQQ (Sim)', color='red')

    # print(f"TQQQ Sim Drawdown: {drawdown_tqqq.idxmin()} {drawdown_tqqq.min():.2f}%")

    plt.show()

"""
ndqcom = web.DataReader('^IXIC', 'yahoo', datetime.datetime(1982, 1, 1), datetime.datetime(2021, 9, 1))['Adj Close']
ndqcom_returns = daily_return(ndqcom).rename('Nasdaq Composite Return %')

# print(df_libor[pd.to_numeric(df_libor.USD1MTD156N, errors='coerce').isnull()])
df_libor = df_libor[df_libor.USD1MTD156N != '.']
df_libor.USD1MTD156N = pd.to_numeric(df_libor.USD1MTD156N)

print(df_libor.head())
print(ndqcom_returns.head())

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
df_libor.plot(ax=ax1)
ax2.plot(ndqcom, color='red')
# ax3.scatter(ndqcom_returns.index, ndqcom_returns, color='green')
ax3.plot(ndqcom_returns, color='green')
ax4.plot(df_libor, color='red')
ax1.set_title('1 Month LIBOR')
ax2.set_title('Nasdaq Composite')
ax3.set_title('Nasdaq Composite Return %')
ax4.set_title('USD1MTD156N')

plt.show()
"""
