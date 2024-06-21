# Python 自動下單小幫手，威力加強版(庫存停損停利GUI應用)

---
> ## **Disclaimer: 範例程式碼及執行檔僅供教學與參考之用，實務交易應自行評估並承擔相關風險**
> 
---

本程式碼為富邦新一代API線上講座範例，示範如何應用Python GUI工具製作自己的庫存停損停利小幫手<br> 
功能涵蓋如下:
* inventory_oco.py<br>
  主要程式，涵蓋介面繪製及停損停利觸價邏輯，須注意本程式範例只涵蓋一般現股庫存的處理，無融資、融券、零股、先賣現沖等功能
* invnetory_oco.spec<br>
  pyinstaller編譯執行檔用的描述檔，如想編出與範例一致的執行檔，需使用本描述檔
     
## 參考連結
富邦新一代API Python SDK載點及開發說明文件
* 新一代API SDK 載點<br>
https://www.fbs.com.tw/TradeAPI/docs/download/download-sdk
* 新一代API 開發說明文件<br>
https://www.fbs.com.tw/TradeAPI/docs/trading/introduction 
* 新一代API 社群討論<br>
https://discord.com/invite/VHjjc4C

## 登入設定
在程式登入畫面中請使用以下設定
> Your ID= #身份證字號<br>
> Password= #交易密碼<br>
> Cert path= #憑證路徑(可使用按鈕選取憑證檔案，會自動帶入路徑)<br>
> Cert Password= #憑證密碼<br>

## 主程式設定
* 主程式僅示範撰寫現股相關停損停利之交易邏輯<br>
* 打勾狀態下即表示有在對該檔庫存的停損停利做監控<br>
* 本範例程式計算之損益報酬率僅使用成交價和庫存均價，未考慮交易成本(稅、手續費)<br>

## Pyinstaller 編譯執行檔設定
建議使用conda指令安裝pyinstaller減少環境問題<br>
```
conda install pyinstaller
```
若想編譯與教學範例一致之執行檔，請先將inventory_oco.py、inventory.spec、inventory.ico三個檔案移至同一資料夾，並用指令如下<br>
```
pyinstaller inventory_oco.spec
```
編譯完成後，應會出現單個執行檔在dist資料夾內<br>
若想由原始碼編譯，建議使用以下指令進行單檔打包，在部署到其他裝置時會比較容易
```
pyinstaller -F inventory_oco.py
```
pyinstaller會自動產生新的inventory_oco.spec，可以再依自己的喜好調整參數
