# app/update_service/main_run.py
from flask import Flask, request
import os
import traceback
from SmartMF import SmartMF # 假設 SmartMF.py 和 serviceAccountKey.json 在同一目錄或可導入

app = Flask(__name__)

# 推薦：為 Cloud Run 設定一個專用的服務帳號，並移除程式碼中的金鑰處理
# 如果不使用專用服務帳號，則確保 serviceAccountKey.json 存在於容器中
SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json"

@app.route('/', methods=['POST', 'GET']) # Cloud Scheduler 通常用 GET 或 POST
def run_stock_update():
    """
    Endpoint to trigger the stock database update.
    Cloud Scheduler will call this endpoint.
    """
    # 可選：添加安全檢查，例如驗證特定的 HTTP 標頭，確保請求來自 Cloud Scheduler
    # scheduler_job_name = request.headers.get("X-CloudScheduler-JobName")
    # scheduler_location = request.headers.get("X-CloudScheduler-Location")
    # if not scheduler_job_name:
    #     print("Warning: Request might not be from Cloud Scheduler.")
        # return "Unauthorized", 401 # 或者只是記錄警告

    print("Cloud Run: Stock update process initiated by scheduler.")
    try:
        # 創建 SmartMF 實例
        # 如果為 Cloud Run 設定了服務帳號，SmartMF 初始化時可以不傳 service_account_key_path
        # firebase_admin.initialize_app() 會自動使用執行環境的服務帳號
        # 這裡我們先保留傳遞路徑的方式，但推薦使用服務帳號
        wallet_updater = SmartMF()

        # 執行更新任務
        wallet_updater.updateStockDB()

        print("Cloud Run: StockDB update process finished successfully.")
        return "Stock database update completed successfully.", 200

    except Exception as e:
        print(f"Cloud Run: An unexpected error occurred during stock update: {e}")
        traceback.print_exc()
        return f"Error during stock update: {str(e)}", 500

if __name__ == "__main__":
    # Cloud Run 會設定 PORT 環境變數
    port = int(os.environ.get("PORT", 8080))
    # 監聽所有網路介面，這是容器化應用程式的標準做法
    app.run(debug=False, host='0.0.0.0', port=port)