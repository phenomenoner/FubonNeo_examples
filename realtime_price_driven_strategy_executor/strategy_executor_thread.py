import time
import threading
import json
import os
from fubon_neo.sdk import FubonSDK
from dotenv import load_dotenv
from datetime import datetime


class StrategyExecutorThread:
    def __init__(self):
        self.sdk = FubonSDK()
        self.accounts = None

        # For threading use
        self.locks = {}  # symbol -> threading lock for symbol
        self.lastest_timestamp = {}  # symbol -> lastest timestamp of trade data

    def login(self, id, pwd, certpath, certpwd):
        """
        The login function
        """
        self.accounts = self.sdk.login(id, pwd, certpath, certpwd)

        return self.accounts

    def run(self, symbols):
        """
        Runs the strategy executor. This function requires prior login.

        Takes a list of stock symbols, subscribes to real-time trade data,
        and executes the strategy each time a new trade data item is received.

        :param symbols: A list of stock symbols to monitor.
        """

        # Check if login is ready
        if self.accounts is None:
            print("請先登入 ...")
            return

        # Connect realtime marketdata
        self.sdk.init_realtime()  # 建立行情連線
        marketdata_ws = self.sdk.marketdata.websocket_client.stock  # 取得連線

        marketdata_ws.on("message", self.__handle_message)
        marketdata_ws.on("connect", lambda: print("行情連線成功"))
        marketdata_ws.on("disconnect", lambda code, msg: print(f"行情斷線. code {code}, msg {msg}"))
        marketdata_ws.on("error", lambda error: print(f"行情連線錯誤訊息: {error}"))

        marketdata_ws.connect()  # 啟用行情連線

        # Initialize threading locks and latest timestamps
        for symbol in symbols:
            self.locks[symbol] = threading.Lock()
            self.lastest_timestamp[symbol] = None

        # 訂閱行情
        for symbol in symbols:
            marketdata_ws.subscribe(
                {
                    'channel': 'trades',
                    'symbol': symbol
                }
            )
        # P.S. 也可以一次訂閱多檔行情
        # marketdata_ws.subscribe(
        #     {
        #         'channel': 'trades',
        #         'symbol': symbols
        #     }
        # )

        # Keep the program running
        while True:
            time.sleep(5)

    def __handle_message(self, message):
        # Process message
        msg = json.loads(message)
        event = msg["event"]
        data = msg["data"]

        if event == "data":
            threading.Thread(target=self.__execute_strategy, args=(data,)).start()
            return

        elif event == "pong" or event == "heartbeat":  # SDK 保持連線用，略過
            return

        elif event == "subscribed":  # 訂閱成功
            print(f"訂閱行情 {data}")
            return

        elif event == "unsubscribed":  # 退訂成功
            print(f"退訂行情 {data}")
            return

        else:  # 其他行情資訊
            print(f"行情資訊 {message}")
            return

    def __execute_strategy(self, data):
        symbol = data["symbol"]
        timestamp = int(data["time"])

        try:
            with self.locks[symbol]:  # 對單一標的，確保同時只執行一筆價格資料，避免策略重複執行
                # Check if this price data is the most recent
                if self.lastest_timestamp[symbol] is None or \
                        self.lastest_timestamp[symbol] < timestamp:
                    self.lastest_timestamp[symbol] = timestamp
                else:
                    return  # 非目前已有之最新資料，略過

                # TODO: 添加交易策略邏輯
                current_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{current_time}] {symbol}, 報價 {data['price']}, 執行策略 ...")
                time.sleep(3)  # Dummy sleep time, for the demonstration purpose only

        except Exception as e:
            print(f"策略執行報錯: symbol {symbol}, error {e}")


# Main script
if __name__ == '__main__':
    print("由 .env 檔案讀取登入資訊 ...")
    load_dotenv()  # Load .env
    id = os.getenv("ID")
    trade_password = os.getenv("TRADEPASS")
    cert_filepath = os.getenv("CERTFILEPATH")
    cert_password = os.getenv("CERTPASSS")

    # 建立 StrategyExecutorThread 物件
    strategy_executor = StrategyExecutorThread()

    # 執行程式
    print("登入 ...")
    accounts = strategy_executor.login(id, trade_password, cert_filepath, cert_password)
    print(f"帳號資訊:\n{accounts}")

    print("啟動策略 ...")
    symbols = ["2330", "2881", "1102"]  # 監控股票列表
    strategy_executor.run(symbols)

