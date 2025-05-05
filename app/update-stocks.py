import time
import traceback
from datetime import datetime
from SmartMF import SmartMF 

if __name__ == "__main__":
    SERVICE_ACCOUNT_KEY = "serviceAccountKey.json" # 確認你的金鑰檔名和路徑
    UPDATE_INTERVAL_SECONDS = 180 # 更新間隔（秒），設為 180 秒 (3 分鐘)

    print(f"Initializing stock price updater with {UPDATE_INTERVAL_SECONDS}s interval...")
    try:
        # 創建 SmartMF 實例 (它會初始化 Firebase)
        wallet_updater = SmartMF() 

        print("Starting infinite update loop (Press Ctrl+C to stop)...")
        while True:
            # 執行更新任務
            wallet_updater.updateStockDB()

            # 等待指定的時間
            print(f"Sleeping for {UPDATE_INTERVAL_SECONDS} seconds...")
            time.sleep(UPDATE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("Updater stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"An unexpected error occurred in the updater: {e}")
        traceback.print_exc()