import time
import multiprocessing
import queue
import json
import os
from fubon_neo.sdk import FubonSDK
from dotenv import load_dotenv


def execute_strategy(price_queue):
    """
    因為使用 multiprocess, 所以交易邏輯函數單獨寫出來
    :param price_queue: multiprocessing.Queue, 報價資料
    """
    while True:
        try:
            data = price_queue.get(timeout=5)  # Blocking get from queue
        except queue.Empty:  # 暫無新行情資料
            continue

        symbol = data["symbol"]

        try:
            # TODO: 添加交易策略邏輯
            print(f"{symbol}, 報價 {data['price']}, 執行策略 ...")
            time.sleep(3)  # Dummy sleep time, for the demonstration purpose only

        except Exception as e:
            print(f"策略執行報錯: symbol {symbol}, error {e}")


class StrategyExecutorMultiprocess:
    def __init__(self):
        self.sdk = FubonSDK()
        self.accounts = None

        # For multiprocess use
        self.price_queue = {}

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

        # Initialize a multiprocessing queue for each symbol
        strategy_process = []
        for symbol in symbols:
            self.price_queue[symbol] = multiprocessing.Queue()
            strategy_process.append(multiprocessing.Process(
                target=execute_strategy,
                args=(self.price_queue[symbol],)
                )
            )

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
        for process in strategy_process:
            process.start()

        for process in strategy_process:
            process.join()

    def __handle_message(self, message):
        # Process message
        msg = json.loads(message)
        event = msg["event"]
        data = msg["data"]

        if event == "data":
            symbol = data["symbol"]
            self.price_queue[symbol].push(data)
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


# Main script
if __name__ == '__main__':
    print("由 .env 檔案讀取登入資訊 ...")
    load_dotenv()  # Load .env
    id = os.getenv("ID")
    trade_password = os.getenv("TRADEPASS")
    cert_filepath = os.getenv("CERTFILEPATH")
    cert_password = os.getenv("CERTPASSS")

    # 建立 StrategyExecutorMultiprocess 物件
    strategy_executor = StrategyExecutorMultiprocess()

    # 執行程式
    print("登入 ...")
    accounts = strategy_executor.login(id, trade_password, cert_filepath, cert_password)
    print(f"帳號資訊:\n{accounts}")

    print("啟動策略 ...")
    symbols = ["2330", "2881", "1102"]  # 監控股票列表
    strategy_executor.run(symbols)

