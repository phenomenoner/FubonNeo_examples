# 當日成交部位 自動停損停利 ( 虛擬 oco )
我們用富邦新一代 API，搭配 Python 來做一個自動抓單的小工具。當你的股票交易成交後，這個程式就會自動幫你把訂單加進監控名單，幫你看著止盈止損。只要碰到設定的價格，程式馬上替你下單，確保你賺的不跑掉，賠的及時止損。這種操作有點像是常見的「自動停損停利單」，一旦一邊成交了，另一邊就不會再執行。<br>

> Disclaimer: 本範例程式碼僅供教學與參考之用，實務交易應自行評估並承擔相關風險

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
