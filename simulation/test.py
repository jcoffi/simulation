import pandas as pd 
import pandas_datareader.data as web
import datetime

import matplotlib.pyplot as plt

def returns(prices):
    """
    Calulates the growth of 1 dollar invested in a stock with given prices
    """
    return (1 + prices.pct_change(1)).cumprod()

def drawdown(prices):
    """
    Calulates the drawdown of a stock with given prices
    """
    rets = returns(prices)
    return (rets.div(rets.cummax()) - 1) * 100

def cagr(prices):
    """
    Calculates the Compound Annual Growth Rate (CAGR) of a stock with given prices
    """
    delta = (prices.index[-1] - prices.index[0]).days / 365.25
    return ((prices[-1] / prices[0]) ** (1 / delta) - 1) * 100

def sim_leverage(proxy, leverage=1, expense_ratio = 0.0, initial_value=1.0):
    pct_change = proxy.pct_change(1)
    pct_change = (pct_change - expense_ratio / 252) * leverage
    sim = (1 + pct_change).cumprod() * initial_value
    sim[0] = initial_value
    return sim

# start = datetime.datetime(2009, 6, 23)
# end = datetime.datetime(2019, 1, 1)
start = datetime.datetime(2010, 2, 11)  # tqqq starts on 2-11-2010
end = datetime.datetime(2021, 9, 1)
start_qqq = datetime.datetime(1999, 3, 10)  # qqq starts on 3-10-1999

# spy = web.DataReader("SPY", "yahoo", start, end)["Adj Close"]
# upro = web.DataReader("UPRO", "yahoo", start, end)["Adj Close"]
#
# spy_returns = returns(spy).rename("SPY")
# upro_returns = returns(upro).rename("UPRO")
#
# spy_returns.plot(title="Growth of $1: SPY vs UPRO", legend=True, figsize=(10,6))
# upro_returns.plot(legend=True)
# plt.show()
#
# print("CAGRs")
# print(f"SPY: {cagr(spy):.2f}%")
# print(f"UPRO: {cagr(upro):.2f}%")

ndqcom = web.DataReader("^IXIC", "yahoo", datetime.datetime(1999, 3, 10), end)["Adj Close"]
# qqq = web.DataReader("QQQ", "yahoo", start, end)["Adj Close"]
# qqq = web.DataReader("QQQ", "yahoo", start_qqq, end)["Adj Close"]
tqqq = web.DataReader("TQQQ", "yahoo", datetime.datetime(2010, 2, 11), end)["Adj Close"]

qqq1 = web.DataReader('QQQ', 'yahoo', datetime.datetime(1999, 3, 10), end)['Adj Close']  # before dot-com
qqq2 = web.DataReader('QQQ', 'yahoo', datetime.datetime(2004, 1, 1), end)['Adj Close']  # after dot-com
qqq3 = web.DataReader('QQQ', 'yahoo', datetime.datetime(2007, 1, 1), end)['Adj Close']  # before 2008 crisis
qqq4 = web.DataReader('QQQ', 'yahoo', datetime.datetime(2010, 2, 11), end)['Adj Close']  # first date of TQQQ

ndqcom_returns = returns(ndqcom).rename('NASDAQ Comp')
tqqq_returns = returns(tqqq).rename('TQQQ Real')
# qqq1_returns = returns(qqq1).rename('QQQ 1')
# qqq2_returns = returns(qqq2).rename('QQQ 2')
# qqq3_returns = returns(qqq3).rename('QQQ 3')
# qqq4_returns = returns(qqq1).rename('QQQ 4')

# ndqcom_returns.plot(title="Growth of $1: NDQCom vs TQQQ", legend=True, figsize=(10,6))
# qqq1_returns.plot(legend=True)

# qqq_sim = sim_leverage(ndqcom, leverage=1.0, expense_ratio=0.002).rename("QQQ Sim (from NDQCom)")
# qqq_sim.plot(legend=True)

'''
Various TQQQ Simulations
'''
# tqqq is 3x qqq, expense ratio of 0.0095
tqqq1_sim = sim_leverage(qqq1, leverage=3, expense_ratio=0.0095).rename("TQQQ Sim 1")
tqqq2_sim = sim_leverage(qqq2, leverage=3, expense_ratio=0.0095).rename('TQQQ Sim 2')
tqqq3_sim = sim_leverage(qqq3, leverage=3, expense_ratio=0.0095).rename('TQQQ Sim 3')
tqqq4_sim = sim_leverage(qqq4, leverage=3, expense_ratio=0.0095).rename('TQQQ Sim 4')

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

fig.suptitle('Growth of $1: Real TQQQ vs. Sim TQQQ\'s')

l1 = ax1.plot(tqqq1_sim)
l2 = ax2.plot(tqqq2_sim)
l3 = ax3.plot(tqqq3_sim)
l4 = ax4.plot(tqqq4_sim)
ax1.set_title('TQQ tracked, 1999-2021')
ax2.set_title('2004-21')
ax3.set_title('2007-21')
ax4.set_title('2010-21')

# plt.legend([l1, l2, l3, l4], ['A', 'B', 'C', 'D'], loc='upper right')

# fig.legend((ax1, ax2, ax3, ax4), ('Sim', 'Real'), 'upper right')

for ax in fig.get_axes():
    ax.label_outer()
    # ax.plot(ndqcom_returns)
    ax.plot(tqqq_returns)
    ax.set_yscale('log')

# tqqq1_sim.plot(legend=True, figsize=(10, 6))
# tqqq2_sim.plot(legend=True, figsize=(10, 6))
# tqqq3_sim.plot(legend=True, figsize=(10, 6))
# tqqq4_sim.plot(legend=True, figsize=(10, 6))
# tqqq_returns.plot(legend=True)

plt.show()

# print("CAGRs")
# print(f"SPY: {cagr(spy):.2f}%")
# print(f"UPRO: {cagr(upro):.2f}%")

'''
Max drawdown ("peak-to-trough decline during a specific period") for different TQQQ simulations
'''

tqqq1_sim_drawdown = drawdown(tqqq1_sim) # from 1999
tqqq2_sim_drawdown = drawdown(tqqq2_sim) # from 2003
tqqq3_sim_drawdown = drawdown(tqqq3_sim) # from 2007
tqqq4_sim_drawdown = drawdown(tqqq4_sim) # real TQQQ

print("Max Drawdown")
print(f"TQQQ 1999- Sim: {tqqq1_sim_drawdown.idxmin()} {tqqq1_sim_drawdown.min():.2f}%")
print(f"TQQQ 2003- Sim: {tqqq2_sim_drawdown.idxmin()} {tqqq2_sim_drawdown.min():.2f}%")
print(f"TQQQ 2007- Sim: {tqqq3_sim_drawdown.idxmin()} {tqqq3_sim_drawdown.min():.2f}%")
print(f"TQQQ 2010- Sim: {tqqq4_sim_drawdown.idxmin()} {tqqq4_sim_drawdown.min():.2f}%")


fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
ax1.plot(tqqq1_sim_drawdown, color="red")
ax2.plot(tqqq2_sim_drawdown, color="red")
ax3.plot(tqqq3_sim_drawdown, color="red")
ax4.plot(tqqq4_sim_drawdown, color="red")
ax1.set_title('TQQQ 1999- Sim drawdown')
ax2.set_title('TQQQ 2003- Sim drawdown')
ax3.set_title('TQQQ 2007- Sim drawdown')
ax4.set_title('TQQQ 2010- Sim drawdown')

# ax1.fill_between(0, tqqq2_sim_drawdown)
# tqqq1_sim_drawdown.plot.area(color="red", title="TQQQ 1999- Sim drawdown", figsize=(10, 6))
# tqqq2_sim_drawdown.plot.area(color="red", title="TQQQ 2003- Sim drawdown", figsize=(10, 6))
# tqqq3_sim_drawdown.plot.area(color="red", title="TQQQ 2007- Sim drawdown", figsize=(10, 6))
# tqqq4_sim_drawdown.plot.area(color="red", title="TQQQ 2010- Sim drawdown", figsize=(10, 6))

plt.show()

'''
Nasdaq Composite vs. TQQQ Sim, 1999-2021
'''

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
fig.suptitle('NDQCom vs TQQQ Sim, 1999-2021')
ax1.plot(ndqcom_returns, 'b-')
ax2.plot(tqqq1_sim_drawdown, 'r-')
ax1.set_xlabel('Date')
ax1.set_ylabel('NDQ Comp', color='b')
ax2.set_ylabel('TQQQ Drawdown', color='r')
# ax1.set_yscale('log')

plt.show()


fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
vix = web.DataReader("^VIX", "yahoo", datetime.datetime(1999, 3, 10), end)["Adj Close"]
fig.suptitle('TQQQ Sim vs VIX, 1999-2021')
ax1.plot(vix, 'g-')
ax2.plot(tqqq1_sim_drawdown, 'r-')
ax1.set_xlabel('Date')
ax1.set_ylabel('VIX', color='g')
ax2.set_ylabel('TQQQ Drawdown', color='r')
# ax1.set_yscale('log')

plt.show()
