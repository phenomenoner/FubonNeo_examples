# 「逐筆洗價」即時交易：多線程、非同步處理與多進程
如果可以在每次價格更新時立即執行交易策略，那麼就能最快的速度來反應市場變化，這就是所謂的「逐筆洗價」概念。

為了達到這種快速反應，系統就必須使用並行處理（Concurrency）。並行處理讓系統能夠同時進行多個任務，這不僅能提升效率，也確保能夠即時處理來自不同商品的數據。在技術上，這通常涉及三種主要的方式：多線程（Threading）、非同步處理（Asyncio）和多進程處理（Multiprocessing）。<br>

> Disclaimer: 本範例程式碼僅供教學與參考之用，實務交易應自行評估並承擔相關風險

## 檔案內容
* strategy_executor_thread.py - 多線程（Threading）版本範例
* strategy_executor_async.py - 非同步處理（Asyncio）版本範例
* strategy_executor_multiprocess.py - 多進程處理（Multiprocessing）版本範例

## 安裝環境
### 安裝套件

```console
pip install -r requirenemts.txt
```

### 安裝富邦新一代API Python SDK

```console
pip install (SDK檔案位置)
```
[富邦新一代API Python SDK 載點](https://www.fbs.com.tw/TradeAPI/docs/download/download-sdk)

## 參考連結
富邦新一代API Python SDK載點及開發說明文件
* 新一代API SDK 載點<br>
https://www.fbs.com.tw/TradeAPI/docs/download/download-sdk
* 新一代API 開發說明文件<br>
https://www.fbs.com.tw/TradeAPI/docs/trading/introduction 
* 新一代API 社群討論<br>
https://discord.com/invite/VHjjc4C
