import threading
import datetime
import time
import os
from dotenv import load_dotenv
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction

global sdk, target_account, restStock, ID, PWDTrade, PWDCert, order_tracker, threading_lock, is_connected, is_update


def trader(filled_no, filled_details, retry_count=0):
    global sdk, target_account, restStock, ID, PWDTrade, PWDCert, order_tracker, threading_lock, is_connected, is_update

    # Check the current price of the stock in the order
    try:
        ticker = restStock.intraday.ticker(symbol=filled_details.stock_no)
        quote = restStock.intraday.quote(symbol=filled_details.stock_no)

        filled_price = float(filled_details.filled_price)
        filled_qty = int(filled_details.filled_qty)
        last_price = float(quote["lastPrice"])
        limit_up_price = float(ticker["limitUpPrice"])
        limit_down_price = float(ticker["limitDownPrice"])

        stop_gain_price = min(limit_up_price, round(filled_price * 1.03))
        stop_loss_price = max(limit_down_price, round(filled_price * 0.97))

        # print(f"{filled_details.stock_no}: limit_up_price {limit_up_price}, limit_down_price {limit_down_price}")

    except (ValueError, TypeError) as e:
        print(f"trader error: {e}")

        if retry_count > 3:
            print(f"Retrieve stock information failed, stock {filled_details.stock_no}, " +
                  f"filled_no {filled_details.filled_no}, too many retries, abort")
            return
        else:
            # Check price failed, retry
            return trader(filled_no, filled_details, retry_count=retry_count + 1)

    # 下停利 (或停損，二擇一) 市價單
    if (last_price >= stop_gain_price) or (last_price <= stop_loss_price):
        # Place buy order
        new_order = Order(
            buy_sell=BSAction.Sell,
            symbol=filled_details.stock_no,
            price=None,
            quantity=filled_qty,
            market_type=MarketType.Common,
            price_type=PriceType.Market,  # 市價單
            time_in_force=TimeInForce.ROD,
            order_type=OrderType.Stock,
        )

        # print(f"{filled_details.stock_no}: last_price {last_price}, stop_gain_price {stop_gain_price}, " +
        #       f"stop_loss_price {stop_loss_price}, filled_price {filled_price}")
        # print(f"new_order: {new_order}\n")

        response = sdk.stock.place_order(target_account, new_order)

        if response.is_success and ((response.data.status == 10) or (response.data.status == 50)):
            with threading_lock:
                order_tracker[filled_no] = [order_tracker[filled_no][0], True]  # 更新委託單監控
                is_update = True  # 顯示資料更新

        elif (response.message is not None) and \
                (("connection" in response.message) or ("login" in response.message)):  # 連線中斷, abort
            with threading_lock:
                is_connected = False
            return

        else:
            print(f"{filled_details.stock_no} 下單失敗, information:")
            if not response.is_success:
                print(response.message)
            else:
                print(response.data)


def login():
    '''
    登入交易主機
    '''
    global sdk, target_account, restStock, ID, PWDTrade, PWDCert, order_tracker, threading_lock, is_connected

    try:
        sdk = FubonSDK()
        accounts = sdk.login(f"{ID}", f"{PWDTrade}", f"./{ID}.pfx", f"{PWDCert}")
        target_account = accounts.data[0]  # 預設選用第一個可用帳號
        print(f"target_account:\n {target_account}\n")

        # 建立行情連線
        sdk.init_realtime()
        restStock = sdk.marketdata.rest_client.stock

        print("連線成功")
        is_connected = True

    except Exception as e:
        print(f"login error {e}")
        time.sleep(5)
        login()


if __name__ == '__main__':
    load_dotenv()

    ID = os.getenv("ID")
    PWDTrade = os.getenv("PWDTrade")
    PWDCert = os.getenv("PWDCert")

    is_connected = False
    login()  # login

    order_tracker = {}  # 監控列表. filled_no -> [FilledData, is_stop_order_sent (True or False)]

    # Initialize threading lock
    threading_lock = threading.Lock()

    # 主要邏輯
    # 說明：每 1 秒進行成交紀錄查詢，若有新的成交紀錄, 則開始監控並下對應之 3% 停損/停利OCO委託單
    # (註: oco委託單統一使用ROD市價單, 效期至收盤為止)
    # (註2: 程式設定查詢運行時間為 9:00AM - 01:25PM)
    # (註3: 本範例僅處理現股整股委託單)

    is_update = True

    while datetime.time(9, 0, 0, 0) <= \
            datetime.datetime.now().time() < \
            datetime.time(13, 25, 0, 0):
        try:
            # Check for connection
            if not is_connected:
                print("重新連線")
                login()

            # Check order results
            current_date_str = datetime.datetime.now().strftime("%Y%m%d")
            response = sdk.stock.filled_history(target_account, current_date_str)
            if not response.is_success:  # 查詢失敗
                if (response.message is not None) and \
                        (("connection" in response.message) or ("login" in response.message)):  # 連線中斷
                    is_connected = False
                    continue

            filled_orders = response.data

            # Update the order tracker
            for order in filled_orders:
                # print(f"order {order}\n")
                if (float(order.filled_qty) >= 1000) and \
                        (order.order_type == OrderType.Stock) and \
                        (order.buy_sell == BSAction.Buy) and \
                        (order.filled_no not in order_tracker):  # 整股現股買單成交且尚未加入監控列表

                    with threading_lock:
                        order_tracker[order.filled_no] = [order, False]
                        is_update = True  # 顯示資料更新

            # Monitor stock price and put buy orders if necessary
            threads = []
            with threading_lock:
                for key, value in order_tracker.items():
                    if not value[1]:
                        thread = threading.Thread(target=trader, args=(key, value[0]))
                        threads.append(thread)
                        thread.start()

                        time.sleep(0.1)

            # Wait until all thread complete
            for t in threads:
                t.join()

        except (ValueError, TypeError) as e:
            print(f"error {e}")
            continue

        # Print out tracking updates
        if is_update:
            active_orders = [key for key, value in order_tracker.items() if not value[1]]
            complete_orders = [key for key, value in order_tracker.items() if value[1]]
            print(datetime.datetime.now().time())
            print(f"監控中成交流水號 (筆數: {len(active_orders)}): {active_orders}")
            print(f"已下停損停利單之對應成交流水號 (筆數: {len(complete_orders)}): {complete_orders}")
            print("\n")

        with threading_lock:
            is_update = False

        time.sleep(1)
