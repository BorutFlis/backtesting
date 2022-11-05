import pandas as pd
import pandas_ta as ta
import yfinance as yf

df = yf.download("BTC-USD", period="60d", interval="15m")

df["sma10"] = df.ta.sma(10)
df["sma30"] = df.ta.sma(30)

df["over"] = df["sma10"] > df["sma30"]
df["cross_up"] = df["over"].ne(df["over"].shift()) & df["over"]
df["cross_down"] = df["over"].ne(df["over"].shift()) & ~df["over"]


in_trade = [False]
trades = []

for i in range(1, len(df)):
    if not in_trade[-1]:
        if df.loc[df.index[i - 1], "cross_up"]:
            in_trade.append(True)
            trades.append([df.index[i]])
        else:
            in_trade.append(False)
    else:
        if df.loc[df.index[i - 1], "cross_down"]:
            in_trade.append(False)
            trades[-1].append(df.index[i])
        else:
            in_trade.append(True)

quantity = 1
fee_rate = 0.0001

trade_df = pd.DataFrame(trades, columns=["start_time", "end_time"])
prices = pd.concat([
            df.loc[trade_df["start_time"], "Open"]
              .reset_index(drop=True),
            df.loc[trade_df["end_time"], "Open"]
              .reset_index(drop=True)
        ], axis=1).set_axis(["start_price", "end_price"], axis=1)

trade_df = pd.concat([trade_df, prices], axis=1)

trade_df["buy_filled"] = quantity * trade_df["start_price"]
trade_df["sell_filled"] = quantity * trade_df["end_price"]

trade_df["buy_fee"] = fee_rate * trade_df["buy_filled"]
trade_df["sell_fee"] = fee_rate * trade_df["sell_filled"]

trade_df["P&L"] = (
        (trade_df["sell_filled"] - trade_df["sell_fee"]) -
        (trade_df["buy_filled"] + trade_df["buy_fee"])
)

trade_df["P&L"].sum()
