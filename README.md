# Gochy 智慧財務管理網頁 - 開發文檔

## 1. 專案概述

**Gochy** 是一個旨在加速記帳流程的網頁應用程式。它允許使用者記錄日常收支、管理個人資產（包括股票和現金），並提供帳本摘要和分析功能。此應用程式利用 Firebase 進行使用者驗證和資料庫儲存，並包含一個後端 API 來處理業務邏輯和一個背景服務來更新股票價格。

## 2. 系統架構

本專案主要由以下幾個部分組成：

* **前端應用程式 (`app/apps`)**: 使用 HTML、CSS 和 JavaScript (`scripts.js`) 構建的單頁應用程式 (SPA)，負責使用者介面和互動。
* **後端 API (`app/main_app`)**: 使用 Flask (`main.py`) 框架和 Python 語言開發，提供 RESTful API 接口供前端調用，處理使用者請求、資料庫操作和業務邏輯。使用 `SmartMF.py` 模組處理核心財務管理邏輯。
* **背景更新服務 (`app/update_service`)**: 一個獨立的 Python 腳本 (`update-stocks.py`)，定期運行以獲取最新的股票價格並更新資料庫。
* **資料庫**: 使用 Google Cloud Firestore 作為主要的資料儲存。
* **使用者驗證**: 使用 Firebase Authentication 進行使用者註冊和登入驗證。

## 3. 後端 API (`app/main_app`)

後端 API 是整個應用的核心，負責處理前端請求和資料庫互動。

### 3.1 主要技術棧

* **框架**: Flask [cite: 3]
* **語言**: Python
* **資料庫互動**: Firebase Admin SDK (`google-cloud-firestore` [cite: 3])
* **使用者驗證**: Firebase Admin SDK (`firebase-admin` [cite: 3])
* **伺服器**: Gunicorn [cite: 1]
* **其他關鍵函式庫**: Requests (HTTP 請求)[cite: 3], lxml (HTML 解析)[cite: 3], Pandas (資料處理) [cite: 3]

### 3.2 核心模組 (`SmartMF.py`)

這個模組封裝了主要的業務邏輯和資料庫操作。

* **`FirestoreClient` 類**:
    * 提供與 Firestore 互動的通用方法，如新增、獲取、更新、刪除文件和集合。
    * 處理 Firebase 初始化和憑證管理。
* **`Expense` 類**:
    * 定義「支出/收入」記錄的資料結構。
    * 包含欄位：日期、項目、金額、支付方式、類別、交易類型、商家、備註、發票號碼。
    * 提供 `to_dict()` 方法將物件轉換為字典。
* **`Asset` 類**:
    * 定義「資產」記錄的資料結構。
    * 包含欄位：項目、目前價值、資產類型、取得日期、取得價值、數量、備註。
    * 提供 `to_dict()` 方法將物件轉換為字典。
* **`SmartMF` 類**:
    * 整合 `FirestoreClient` 進行具體的業務操作。
    * 提供使用者管理方法（新增、獲取）。
    * 提供支出/收入記錄管理方法（新增、更新、刪除、按日期範圍查詢、獲取月度記錄）。
    * 提供資產管理方法（新增、更新、刪除、獲取所有資產、按名稱查找）。
    * 提供帳本管理功能（建立個人/共享帳本、獲取使用者帳本列表）。
    * 提供摘要數據計算方法 (`get_summary_data`)，用於計算總資產、總負債、各類分佈等。
    * 包含與股票相關的方法（`get_current_price` - 雖然定義為全域，但在 `SmartMF` 中被使用、`add_stocks_to_List`、`get_stockDB`、`updateStockDB`、`updateStockPrice`）。
    * 管理使用者選項（交易類型、資產類型）。

### 3.3 API 端點 (`main.py`)

API 使用 Flask 框架建立，並透過 `@firebase_token_required` 裝飾器保護需要使用者登入的端點。此裝飾器會驗證請求標頭中的 Firebase ID Token。

| 方法   | 路徑                              | 描述                                       | 認證       |
| :----- | :-------------------------------- | :----------------------------------------- | :--------- |
| POST   | `/api/createUserProfile`          | 註冊成功後，在 Firestore 建立使用者 Profile   | Firebase Token |
| GET    | `/`                               | 列出所有 API 端點                            | 無         |
| GET    | `/api/accounts`                   | **(已過時?)** 獲取所有使用者帳戶列表         | 無         |
| GET    | `/api/home`                       | 獲取使用者首頁總資產                         | Firebase Token |
| GET    | `/api/options`                    | 獲取使用者自訂的交易與資產類別選項           | Firebase Token |
| GET    | `/api/stocks`                     | 獲取使用者的股票/證券資產資料                | Firebase Token |
| GET    | `/api/assets`                     | 獲取使用者的非股票/證券資產資料              | Firebase Token |
| PUT    | `/api/asset/<asset_id>`           | 更新指定 ID 的資產資料                       | Firebase Token |
| POST   | `/api/changeInventory`            | **(已過時?)** 更新庫存 (買入/賣出股票)       | Firebase Token |
| POST   | `/api/submitAccount`              | 提交一筆新的支出或收入記錄                   | Firebase Token |
| POST   | `/api/submitStock`                | 提交一筆新的資產記錄 (包含股票和其他)        | Firebase Token |
| GET    | `/api/getRecords`                 | **(已過時?)** 獲取記帳記錄 (分頁)            | Firebase Token |
| GET    | `/api/totals`                     | **(已過時?)** 獲取當月總收支                 | Firebase Token |
| PUT    | `/api/record/<record_id>`         | 更新指定 ID 的支出或收入記錄                 | Firebase Token |
| DELETE | `/api/record/<record_id>`         | 刪除指定 ID 的支出或收入記錄                 | Firebase Token |
| POST   | `/api/editAsset`                  | **(已過時?)** 編輯資產                       | Firebase Token |
| GET    | `/api/getDailyHistory`            | **(已過時?)** 獲取當天歷史記錄               | Firebase Token |
| GET    | `/api/getSummaryData`             | 獲取指定日期的摘要數據 (總覽、分佈等)        | Firebase Token |
| GET    | `/api/recordsByDateRange`         | 獲取指定日期範圍內的記帳記錄                 | Firebase Token |
| POST   | `/api/aiSuggestion`               | **(註解中)** 獲取 AI 財務建議              | Firebase Token |
| GET    | `/api/user/profile`               | 獲取當前登入使用者的 Firestore Profile 資料 | Firebase Token |
| GET    | `/api/ledgers`                    | 獲取當前使用者擁有的個人與共享帳本列表         | Firebase Token |
| POST   | `/api/ledgers`                    | 建立新的個人或共享帳本                       | Firebase Token |
| GET    | `/api/split_group/<group_id>/members` | 獲取指定共享帳本的成員列表                 | Firebase Token |

**注意**: 部分 API 端點 (標記為已過時) 的功能可能已被其他端點取代或不再使用，建議根據前端 `scripts.js` 的實際調用情況確認。

### 3.4 認證機制

* API 使用 Firebase Authentication 進行使用者身份驗證。
* 前端在使用者登入後獲取 Firebase ID Token。
* 前端調用受保護的 API 時，需在 HTTP 請求的 `Authorization` 標頭中攜帶 `Bearer <ID_Token>`。
* 後端的 `@firebase_token_required` 裝飾器負責驗證此 Token，並將驗證通過的使用者 UID (`g.uid`) 存儲在 Flask 的 `g` 物件中，供後續路由使用。

## 4. 資料庫 (Firestore)

應用程式使用 Firestore 作為 NoSQL 資料庫。根據 `SmartMF.py` 的程式碼推斷，可能的資料庫結構如下：

* **`UserDB` (集合)**: 儲存所有使用者資料。
    * **`<user_id>` (文件)**: 以 Firebase Auth UID 作為文件 ID。
        * `username`: 使用者名稱
        * `email`: 電子郵件
        * `created_at`: 建立時間
        * `access`: 權限等級 (可能未使用)
        * `ledgers`: (Map) 包含使用者帳本列表
            * `personal`: (Array) 個人帳本名稱列表
            * `shared`: (Array of Maps) 共享帳本列表，每個 Map 包含 `invite_code` 和 `name`
        * **`expenses` (子集合)**: 儲存該使用者的**預設**支出/收入記錄。
            * **`<expense_id>` (文件)**: 文件內容符合 `Expense` 類結構。
        * **`<ledger_name>` (子集合)**: 儲存使用者**自訂的個人**帳本的支出/收入記錄 (如果 `ledgers.personal` 存在)。
            * **`<expense_id>` (文件)**: 文件內容符合 `Expense` 類結構。
        * **`assets` (子集合)**: 儲存該使用者的資產記錄。
            * **`<asset_id>` (文件)**: 文件內容符合 `Asset` 類結構。
        * **`options` (子集合)**: 儲存使用者自訂選項。
            * **`options` (文件)**: 包含 `transactionType` 和 `assetType` 的 Map。
        * **`relationship` (子集合)**: (用途待確認，目前為空)
* **`PublicLedgerDB` (集合)**: 儲存共享帳本的資訊。
    * **`<invite_code>` (文件)**: 以邀請碼 (group_id) 作為文件 ID。
        * `name`: 共享帳本名稱
        * `creator_uid`: 建立者 UID
        * `creator_name`: 建立者名稱
        * `members`: (Map) 成員名稱及其目前分攤狀態 (例如 `{ "userA": 0, "userB": 0 }`)
        * `create_at`: 建立時間
        * **`expenses` (子集合)**: 儲存該共享帳本的支出/收入記錄。
            * **`<expense_id>` (文件)**: 文件內容符合 `Expense` 類結構，可能包含 `member` 欄位指明歸屬成員。
* **`StockDB` (集合)**: 儲存需要追蹤價格的股票代碼及其目前價格。
    * **`<stock_symbol>` (文件)**: 以股票代碼 (例如 "2330") 作為文件 ID。
        * `item`: 股票代碼
        * `current_price`: 目前價格

## 5. 前端應用程式 (`app/apps`)

前端是一個單頁應用程式 (SPA)，負責使用者介面展示和互動。

* **`index.html`**: 應用程式的主要 HTML 結構，定義了各個頁面區塊 (`<section class="page">`) 和底部導航欄。包含登入、註冊、編輯記錄、編輯資產和新增帳本的模態框 (Modal)。
* **`styles.css`**: 定義應用程式的視覺樣式，包括顏色、佈局、卡片樣式、表單樣式、按鈕樣式等。使用了 CSS 變數來管理顏色主題。
* **`scripts.js`**: 核心的 JavaScript 檔案，處理以下功能：
    * Firebase 初始化和使用者驗證狀態監聽 (`onAuthStateChanged`)。
    * 處理登入、註冊邏輯，與後端 API 互動。
    * 實現 SPA 頁面切換邏輯 (`handleHashChange`)。
    * 從後端 API (`WorkspaceWithAuth`) 獲取資料 (總資產、股票、資產、摘要、記錄等)。
    * 將獲取的資料渲染到對應的 HTML 元素中 (例如，資產卡片、記錄列表)。
    * 處理表單提交 (記帳、資產)，調用後端 API。
    * 實現圖表繪製 (使用 Chart.js) 來展示資產和開銷分佈。
    * 處理股票/資產卡片的買入/賣出/編輯按鈕交互。
    * 處理記錄列表的編輯/刪除按鈕交互。
    * 處理帳本切換邏輯，包括更新 UI 和重新載入對應帳本數據。
    * 處理新增帳本 Modal 的交互邏輯。
    * 與後端 AI 建議 API 互動。

## 6. 背景更新服務 (`app/update_service`)

此服務用於定期更新股票價格。

* **`update-stocks.py`**:
    * 使用 `SmartMF` 模組 與 Firestore 互動。
    * 定期 (預設 180 秒) 調用 `SmartMF.updateStockDB()` 方法。
    * `updateStockDB()` 方法會讀取 `StockDB` 集合中的股票列表，透過 `get_current_price` 函數 (內部調用 Yahoo Finance) 獲取最新價格，然後更新回 `StockDB`。

**注意**: 前端在需要顯示最新股票價格時 (例如在 `/api/stocks` 端點)，會觸發後端調用 `SmartMF.updateStockPrice(uid)`，此方法會讀取 `StockDB` 的最新價格來更新使用者 `assets` 子集合中對應股票的 `current_price` 和 `current_amount`。背景服務 (`update-stocks.py`) 負責更新 `StockDB`，而前端請求觸發的 `updateStockPrice` 負責將 `StockDB` 的價格同步到使用者資產中。

## 7. 設定與部署

### 7.1 依賴項目

主要的 Python 依賴項目列在 `requirements.txt` [cite: 3] 中，包括：

* Flask, Gunicorn
* firebase-admin, google-cloud-firestore, google-auth
* requests, lxml, beautifulsoup4
* pandas, numpy

前端依賴：

* Bootstrap (CSS & JS)
* Bootstrap Icons
* jQuery
* Bootstrap Datepicker
* Firebase JS SDK (app, auth)
* Chart.js

### 7.2 設定檔

* **`app.yaml` ([cite: 1] 或)**: Google App Engine 的設定檔。
    * 指定 Python 執行環境 (`python312`)。
    * 指定實例類型 (`F1`)。
    * 定義應用程式入口點 (`entrypoint: gunicorn -b :$PORT main:app`)。
    * 設定靜態檔案處理 (`handlers`)。
    * 設定自動擴展 (`automatic_scaling`)。
* **`serviceAccountKey.json` (未提供，但程式碼中引用)**: Firebase Admin SDK 所需的服務帳號金鑰檔案。**此檔案包含敏感憑證，切勿提交到版本控制系統中。**
* **Firebase 設定 (`scripts.js`)**: 前端 Firebase SDK 的初始化設定，包含 API Key、Auth Domain 等。

### 7.3 部署

該應用程式設計為部署在 Google App Engine 上。

1.  **準備 `serviceAccountKey.json`**: 從 Firebase 專案設定中下載服務帳號金鑰，並將其放置在專案的適當位置 (確保後端和更新服務可以讀取到)。**不要提交此檔案到 Git。**
2.  **安裝依賴**: `pip install -r requirements.txt`
3.  **部署主應用**: 使用 Google Cloud SDK 部署 `app/main_app` 目錄下的應用：`gcloud app deploy app/main_app/app.yaml` (可能需要調整路徑)。
4.  **部署/運行更新服務**:
    * **App Engine Service**: 可以將 `app/update_service` 作為一個獨立的 App Engine 服務進行部署，設定其為背景服務或使用 Cron Job 觸發。
    * **其他方式**: 也可以在 VM、Cloud Run 或其他計算環境中運行 `update-stocks.py` 腳本。

---
