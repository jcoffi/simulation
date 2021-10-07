from datetime import datetime, timedelta

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

from utils import daily_return, process_libor, compound_return


AVG_TRADING_DAYS_PER_YEAR = 252


def daily_leveraged_etf(etf_prices, daily_libor, starting_amount=1.0, leverage=1.0, expense_ratio=0.2):
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

    lev_etf = lev_return - etf_expense  # subtract etf_expense
    lev_etf = lev_etf.subtract(leverage_expense, axis=0)  # subtract lev_expense on index
    # since some etf_prices skip a lot of data in the 1980s (but LIBOR is fully logged), remove all NaN
    lev_etf = lev_etf.dropna()

    #
    # TODO: Account for trading fee & slippage
    #

    # Compound gain/loss with starting amount
    df_compound = compound_return(lev_etf, starting_amount=starting_amount, base_col='Close')
    # df_compound.index = lev_etf.index
    lev_etf = pd.concat([lev_etf, df_compound], axis=1)  # adds 'Investment' column to lev_etf

    return lev_etf

if __name__ == '__main__':
    libor_inception_date = datetime(1986, 1, 2)
    libor_inception_prev_date = libor_inception_date - timedelta(days=2)  # Jan 1 is market holiday, so get 1985-12-31
    last_data_date = datetime(2021, 10, 1)  # get until Oct 1, 2021
    # first_data_date = datetime(1986, 1, 2)
    # first_data_date = datetime(1992, 1, 2)
    first_data_date = datetime(2010, 2, 9)
    tqqq_inception_date = datetime(2010, 2, 9)

    df_libor = process_libor('../dataset/USD1MTD156N.csv')

    #
    # NASDAQ Composite - index TQQQ follows
    #
    ndqcom = web.DataReader('^IXIC', 'yahoo', first_data_date, last_data_date)['Adj Close']
    df_ndqcom = pd.DataFrame(data={'Close': ndqcom})

    #
    # Actual TQQQ data from 2010
    #
    tqqq_actual = web.DataReader('TQQQ', 'yahoo', tqqq_inception_date, last_data_date)['Adj Close']

    #
    # Simulate TQQQ (ER is 0.95%)
    #
    tqqq_returns = daily_leveraged_etf(df_ndqcom, daily_libor=df_libor['Value'], leverage=3,
                                       expense_ratio=0.95, starting_amount=1.5)

    # print(tqqq_returns)
    # Some number crunching and visualization
    tqqq_combined = pd.DataFrame(columns=['NDQ %', 'Actual TQQQ %', 'Sim TQQQ %', 'Ratio (Actual)', 'Ratio (Sim)'])
    tqqq_combined['NDQ %'] = df_ndqcom[-21:].pct_change(1)[1:] * 100
    tqqq_combined['Actual TQQQ %'] = tqqq_actual[-21:].pct_change(1)[1:] * 100
    tqqq_combined['Sim TQQQ %'] = tqqq_returns['Close'][-20:] * 100
    # tqqq_combined['Diff'] = tqqq_combined['Actual TQQQ %'] - tqqq_combined['Sim TQQQ %']
    tqqq_combined['Ratio (Actual)'] = tqqq_combined['Actual TQQQ %'] / tqqq_combined['NDQ %']
    tqqq_combined['Ratio (Sim)'] = tqqq_combined['Sim TQQQ %'] / tqqq_combined['NDQ %']
    tqqq_combined.dropna()
    print(tqqq_combined)

    # Visualization for TQQQ Ratio in Actual vs. Sim
    tqqq_ratios = pd.DataFrame(columns=['NDQ %', 'Ratio (Actual)', 'Ratio (Sim)'])
    tqqq_ratios['NDQ %'] = df_ndqcom.pct_change(1)
    tqqq_ratios['Ratio (Actual)'] = abs(tqqq_actual.pct_change(1)[1:] / tqqq_ratios['NDQ %'])
    tqqq_ratios['Ratio (Sim)'] = abs(tqqq_returns['Close'] / tqqq_ratios['NDQ %'])
    tqqq_ratios.dropna()
    tqqq_ratios = tqqq_ratios.clip(upper=10, lower=-10)
    # tqqq_ratios['Ratio (Actual)'].where(tqqq_ratios['Ratio (Actual)'] <= 10, 10)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    scatter_size = (2,)
    ax1.title.set_text('NDQ to TQQQ Ratio (abs)')
    ax1.scatter(tqqq_ratios.index, tqqq_ratios['Ratio (Actual)'], label='TQQQ (Actual)', s=scatter_size)
    ax1.scatter(tqqq_ratios.index, tqqq_ratios['Ratio (Sim)'], label='TQQQ (Sim)', s=scatter_size)
    # tqqq_ratios['Ratio (Actual)'].plot(ax=ax1, label='TQQQ (Actual)')
    # tqqq_ratios['Ratio (Sim)'].plot(ax=ax1, label='TQQQ (Sim)')

    ax2.title.set_text('TQQQ Result')
    # plt.plot(tqqq_returns.index, tqqq_returns['Investment'], label='TQQQ (Sim)')
    tqqq_returns['Investment'].plot(ax=ax2, label='TQQQ (Sim)')
    tqqq_actual.plot(ax=ax2, label='TQQQ (Real)')

    # for ax in fig.axes():
    #     ax.legend()
    ax1.legend()
    ax2.legend()

    plt.gca()
    plt.show()
