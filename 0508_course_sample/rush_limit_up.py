#%%
import os 
from dotenv import load_dotenv

load_dotenv(override=True)
id = os.getenv('ID')
pwd = os.getenv('PWD')
cert_filepath = os.getenv('CPATH')
certpwd = os.getenv('CPWD')

target_account = os.getenv('ACCOUNT')
dev_server = os.getenv('SERVER')

# %%

from fubon_neo.sdk import FubonSDK, Order

sdk = FubonSDK(dev_server)
response = sdk.login(id, pwd, cert_filepath, certpwd)  # 需登入後，才能取得行情權限

# 更新可用帳號列表
accounts = response.data

# 設定啟用帳號
active_account = None
for account in accounts:
    if target_account == account.account:
        active_account = account
        break

if active_account is not None:
    print(f"當前使用帳號\n{active_account}")

sdk.init_realtime() # 建立行情連線
reststock = sdk.marketdata.rest_client.stock


# %%
import pandas as pd
from datetime import datetime

last_close_dict = {}
subscribed_list = []
watch_percent = 6

open_time = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0)
open_unix = int(datetime.timestamp(open_time)*1000000)

def monitor_n_subscribe():
    TSE_movers = reststock.snapshot.movers(market='TSE', type='COMMONSTOCK', direction='up', change='percent', gte=watch_percent)
    TSE_movers_df = pd.DataFrame(TSE_movers['data'])
    OTC_movers = reststock.snapshot.movers(market='OTC', type='COMMONSTOCK', direction='up', change='percent', gte=watch_percent)
    OTC_movers_df = pd.DataFrame(OTC_movers['data'])

    all_movers_df = pd.concat([TSE_movers_df, OTC_movers_df])
    all_movers_df = all_movers_df[all_movers_df['lastUpdated']>open_unix]
    
    all_movers_df = all_movers_df[all_movers_df['tradeVolume']>500]
    all_movers_df = all_movers_df[all_movers_df['closePrice']<1000]
    all_movers_df = all_movers_df[all_movers_df['closePrice']>10]
    
    all_movers_df['last_close'] = all_movers_df['closePrice']-all_movers_df['change']

    last_close_dict.update(dict(zip(all_movers_df['symbol'], all_movers_df['last_close'])))

    new_subscribe = list(all_movers_df['symbol'])
    new_subscribe = list(set(new_subscribe).difference(set(subscribed_list)))
    print("NEW UP SYMBOL:", new_subscribe)
    if new_subscribe:
        stock.subscribe({
            'channel': 'trades',
            'symbols': new_subscribe
        })
    
        subscribed_list.extend(new_subscribe)

    

# %%
from fubon_neo.sdk import Order
from fubon_neo.constant import OrderType, TimeInForce, PriceType, MarketType, BSAction
import json

trigger_percent = 9
stop_loss_percent = 7
position_dict = {}

def on_filled(err, content):
    if content.user_def == "RLU_IN":
        position_dict[content.stock_no] = 1
        print("RLU buy in", content.stock_no)
    elif content.user_def == "RLU_OUT":
        print("RLU stop loss", content.stock_no)
        
sdk.set_on_filled(on_filled)

subscribed_ids = {}
ordered_ids = []

def handle_message(message):
    msg = json.loads(message)
    event = msg["event"]
    data = msg["data"]
    
    # subscribed事件處理
    if event == "subscribed":
        for subscribed_item in data:
            id = subscribed_item["id"]
            symbol = subscribed_item["symbol"]
            print("successfully subscribed", symbol)
            subscribed_ids[symbol] = id
    
    # data事件處理
    elif event == "data":
        symbol = data["symbol"]
        cur_price = data["price"]
        change_percent = (cur_price - last_close_dict[symbol])/last_close_dict[symbol]*100
        
        if change_percent >= trigger_percent and symbol not in ordered_ids:
            print("RUSH", "data:", symbol, "cur_price", cur_price, "last_close", last_close_dict[symbol], "pct:", change_percent)
            order = Order(
                buy_sell=BSAction.Buy,
                symbol=symbol,
                price=None,
                quantity=1000,
                market_type=MarketType.Common,
                price_type=PriceType.Market,
                time_in_force=TimeInForce.ROD,
                order_type=OrderType.Stock,
                user_def="RLU_IN"
            )

            # 下單
            response = sdk.stock.place_order(active_account, order)
            print(f"下單回報, 股票代碼 {symbol}:\n{response}\n")
            ordered_ids.append(symbol)
            
        elif change_percent < stop_loss_percent and symbol in position_dict:
            if position_dict[symbol] == 1:
                print("STOPLOSS", symbol, "cur_price", cur_price, "pct:", change_percent)
                order = Order(
                    buy_sell=BSAction.Sell,
                    symbol=symbol,
                    price=None,
                    quantity=1000,
                    market_type=MarketType.Common,
                    price_type=PriceType.Market,
                    time_in_force=TimeInForce.ROD,
                    order_type=OrderType.Stock,
                    user_def="RLU_OUT"
                )

                # 下單
                response = sdk.stock.place_order(active_account, order)
                print(f"下單回報, 股票代碼 {symbol}:\n{response}\n")
                position_dict[symbol] = 0
            
    # print(msg)

stock = sdk.marketdata.websocket_client.stock
stock.on('message', handle_message) # 註冊callback function
stock.connect() # 啟動連結

# %%
from threading import Timer

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

timer = RepeatTimer(1, monitor_n_subscribe)
timer.start()
# %%
