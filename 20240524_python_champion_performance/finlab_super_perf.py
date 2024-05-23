#%%
from finlab import data
close = data.get('price:收盤價')
close
# %%

condition0 = close > close.rolling(50).mean()
condition1 = close > close.rolling(150).mean()
condition2 = close > close.rolling(200).mean()
condition3 = close.rolling(20).mean() > close.rolling(200).mean()
condition4 = close.rolling(50).mean().rise().sustain(20, 15)
condition5 = close.rolling(20).mean() > close.rolling(200).mean()
condition6 = close.rolling(50).mean() > close.rolling(150).mean()
condition7 = close > close.rolling(250).min() * 1.25
condition8 = close < close.rolling(250).max() * 1.25
condition9 = ((close - close.rolling(20).mean()) / close.rolling(20).std()).rank(axis=1, pct=True) > 0.7

# %%

import pandas as pd
from finlab.tools.event_study import create_factor_data

ic = []
conditions = [condition0, condition1, condition2, condition3, condition4, condition5, condition6, condition7, condition8, condition9]
for i, condition in enumerate(conditions):
    print('calculate factor data', i)

    # 計算 IC(information coefficient)
    fdata = create_factor_data(condition, data.get('etl:adj_close'))
    ic.append(fdata.corr()['factor_factor'][['5D', '10D', '20D', '60D']])

# 繪製色溫圖
pd.DataFrame(ic).reset_index(drop=True).round(3).style.background_gradient()
# %%

# 導入 finlab 回測模組
from finlab import backtest

# 這行代碼結合前面定義的多個條件（condition0 到 condition9）來形成一個綜合的持倉條件。
# 只有當所有這些條件同時滿足時，`position` 變量才會是真（True）。

position = condition0 & condition1 & condition2 & condition3 & condition4 & condition5 & condition6 & condition7 & condition8 & condition9

# 這行代碼使用 backtest.sim 函數執行回測：
# * position['2020':] 指定從2020年開始的數據用於回測。
# * resample='Q' 表示數據將按季度重新取樣。
# * position_limit=0.1 設定每個資產的最大持倉比例為10%。
# * upload=False 表示回測結果不上傳到任何服務或數據庫。

r = backtest.sim(position['2020':], resample='Q', position_limit=0.1, upload=False)

# 使用 display() 函數來顯示回測的結果，如總回報率、夏普比率等重要指標。
r.display()
# %%

import numpy as np
from finlab import data, backtest

close =  data.get('price:收盤價')
volume = data.get('price:成交股數')
rev = data.get('monthly_revenue:當月營收')

# 財務數據
fundamental = rev.pct_change().average(6) > 0

# 趨勢樣版
trend_template = close > close.average(250)

# 通道狹窄
band_contract = close.rolling(20).min() > close.rolling(20).max() * 0.7

# 成交量下降
volume_reduce = volume.average(10) < (volume.average(60)*0.5)

# 通道收縮
price_contract = close.rolling(10).std() < (close.rolling(60).std()*0.5)

# VCP = 價量收縮、創新高、有足夠成交量
vcp = (volume_reduce & price_contract & band_contract).sustain(5, 1)

new_high = (close == close.rolling(100).max()) & (volume >= volume.rolling(20).mean()*0.8)

# 總體部位
# 進場：(c1, c2, vcp, 流動性足夠, 長期均向上)
# 出場：股價 < 季線
buy = (fundamental & trend_template & vcp & new_high & (volume * close > 2000000))
sell = close < close.average(60)

vcp_position = buy.hold_until(sell, rank=rev.pct_change(), nstocks_limit=5)

# 回測
r = backtest.sim(vcp_position.loc['2020':], position_limit=0.2, resample='W', stop_loss=0.1)
# %%
from finlab.online.order_executor import Position

# total fund
fund = 1000000
position = Position.from_report(r, fund)

# 取得目標部位
new_pos_list = position.position
new_pos_list
# %% 獲取登入資訊
from dotenv import load_dotenv
import os

load_dotenv(override=True)

id = os.getenv("ID")
pwd = os.getenv("PWD")
cert_filepath = os.getenv('CPATH')
certpwd = os.getenv('CPWD')

#%% 登入並取得帳戶
from fubon_neo.sdk import FubonSDK, Order

sdk = FubonSDK()
   
accounts = sdk.login(id, pwd, cert_filepath, certpwd)
active_account = accounts.data[0]
print(active_account)

#%% 轉換新目標部位格式，及讀取舊的部位

import json 

# 新目標部位格式轉換
new_pos_dict = {}
for new_pos in new_pos_list:
    new_pos_dict[new_pos['stock_id']] = new_pos['quantity']

# 舊部位如果存在讀取舊的部位
old_pos_dict = {}
if os.path.isfile(".\\old_pos.json"):
    print('load old pos...')
    with open("old_pos.json", "r") as pos_file: 
        old_pos_text = pos_file.read()
        old_pos_dict = json.loads(old_pos_text)
        print(old_pos_dict)

#%% 舊部位做賣出，新部位做買進
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction

# 比對新部位做賣出動作
print('Selling old position...')
for stock_id, sell_num in old_pos_dict.items():
    
    sell_qty = sell_num*1000

    if stock_id in new_pos_dict:
        sell_qty = sell_qty-new_pos_dict[stock_id]*1000

    if sell_qty>0:
        print(stock_id, 'sell target:', sell_num, 'sell:', sell_qty)
        order = Order(
            buy_sell = BSAction.Sell,
            symbol = stock_id,
            price =  None,
            quantity =  sell_qty,
            market_type = MarketType.Common,
            price_type = PriceType.Market,
            time_in_force = TimeInForce.ROD,
            order_type = OrderType.Stock,
            user_def = "super" # optional field
        )

        res = sdk.stock.place_order(active_account, order)
        print(res)
    else:
        print(stock_id, "新部位保留")

#%% 比對舊部位做買進動作
print('Buying new position...')
for stock_id, buy_num in new_pos_dict.items():
    
    buy_qty = buy_num*1000

    if stock_id in old_pos_dict:
        buy_qty = buy_qty-old_pos_dict[stock_id]*1000

    if buy_qty>0:
        print(stock_id, 'buy target:', buy_num, 'buy:', buy_qty)
        order = Order(
            buy_sell = BSAction.Buy,
            symbol = stock_id,
            price =  None,
            quantity =  buy_qty,
            market_type = MarketType.Common,
            price_type = PriceType.Market,
            time_in_force = TimeInForce.ROD,
            order_type = OrderType.Stock,
            user_def = "super" # optional field
        )

        res = sdk.stock.place_order(active_account, order)
        print(res)
    else:
        print(stock_id, "張數已滿足")

#%% 新目標部位存檔為舊部位
with open("old_pos.json", "w") as out_file: 
    json.dump(new_pos_dict, out_file)

# %%
