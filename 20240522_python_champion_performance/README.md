# Python在台股上應用超級績效
> **Disclaimer: 範例程式碼僅供教學與參考之用，實務交易應自行評估並承擔相關風險**
> 
本程式碼為富邦新一代API與FinLab合作之線上講座範例，示範如何使用FinLab之Python套件工具量化「超級績效」所提及的交易策略 
功能涵蓋如下:
* 超級績效台股版教學.ipynb<br>
  1. 應用finlab套件 + colab 產生超級績效趨勢樣板回測結果
  2. 應用finlab套件 + colab 產生超級績效完整策略(趨勢樣板+VCP)回測結果

* finlab_super_perf.py<br>
  1. 應用finlab套件產生超級績效趨勢樣板回測結果
  2. 應用finlab套件產生超級績效完整策略(趨勢樣板+VCP)回測結果
  3. 串接富邦新一代API做自動下單
     
## 參考連結
富邦新一代API Python SDK載點及開發說明文件
* 新一代API SDK 載點<br>
https://www.fbs.com.tw/TradeAPI/docs/download/download-sdk
* 新一代API 開發說明文件<br>
https://www.fbs.com.tw/TradeAPI/docs/trading/introduction 
* 新一代API 社群討論<br>
https://discord.com/invite/VHjjc4C
* FinLab 財經實驗室<br>
https://www.finlab.tw/

## 登入設定 (finlab_super_perf.py)
在程式資料夾中新建檔案 `.env` 並輸入以下內容<br>
> ID= #身份證字號<br>
> PWD= #交易密碼<br>
> CPATH= #憑證路徑<br>
> CPWD= #憑證密碼<br>
