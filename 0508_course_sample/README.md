# Python搶漲停程式範例框架
> Disclaimer: 範例程式碼僅供教學與參考之用，實務交易應自行評估並承擔相關風險
> 
本範例提供如何應用富邦 **新一代API【行情快照】** 與串接 **新一代API WebSocket【即時報價】** 功能，製作Python搶漲停程式的基本框架<br>
功能涵蓋如下:
1. 每秒應用行情快照抓出全市場漲幅較大個股票
2. 漲幅較大的股票串接即時報價監控是否達下單門檻
3. 達門檻標的送出市價委託，並串接成交主動回報紀錄部位
4. 依據部位紀錄做即時報價停損控制

## 參考連結
富邦新一代API Python SDK載點及開發說明文件
* 新一代API SDK 載點<br>
https://www.fbs.com.tw/TradeAPI/docs/download/download-sdk
* 新一代API 開發說明文件<br>
https://www.fbs.com.tw/TradeAPI/docs/trading/introduction 
* 新一代API 社群討論<br>
https://discord.com/invite/VHjjc4C

## 登入設定
在程式資料夾中新建檔案 `.env` 並輸入以下內容<br>
> ID= #身份證字號<br>
> PWD= #交易密碼<br>
> CPATH= #憑證路徑<br>
> CPWD= #憑證密碼<br>
> ACCOUNT= #帳號<br>
