# FinQA-RAG：金融問答高精準檢索系統

本專案提供一個完整的金融領域問答檢索系統，透過混合檢索（Hybrid Search）與重排序（Reranking）技術，實現高精度的答案檢索，特別適合用於大型金融資料庫的問答應用。

## 專案目標

- 從金融、保險產品資訊及銀行業務問答集中快速找到問題最相關的答案。
- 使用混合檢索（語意 + 關鍵字）技術，搭配深度重排序技術，達成精確的答案檢索。
- 提供易用的 API 介面，方便系統整合。

## 技術說明

### 核心技術

- **Hybrid Search (混合檢索)**
  - 使用 OpenAI Embedding 模型 (`text-embedding-3-large`) 進行語意搜尋。
  - 搭配 BM25 演算法進行關鍵字搜尋，兼顧語意與詞彙匹配。
- **Reranking (重排序)**
  - 使用 Voyage AI Reranker 模型 (`rerank-2`) 對檢索出的候選答案進行二次重排序，精準篩選出最相關的答案。

### 專案架構

```
.
├─ data/                 # 存放問題與答案、參考資料
├─ docker/               # Weaviate 向量資料庫部署
├─ src/
│  └─ esun_finrag/
│     ├─ api.py                # FastAPI API 介面
│     ├─ retriever.py          # 混合檢索及重排序核心程式
│     ├─ settings.py           # 系統設定與紀錄工具
│     └─ datastore/
│        └─ weaviate_client.py # Weaviate 資料庫連線管理
│
├─ scripts/
│  ├─ run_predict.py           # 預測與生成答案檔案的腳本
│  └─ ingest/
│     ├─ ingest_reference.py   # 將資料匯入至 Weaviate
│     └─ pdf_tools.py          # PDF 資料處理工具
│
├─ tests/                      # 測試程式
├─ README.md                   # 專案文件（即本文件）
├─ pyproject.toml              # 專案依賴管理
├─ .pre-commit-config.yaml     # 程式碼格式化工具
└─ .ruff.toml                  # 程式碼風格設定
```

## 環境建置

### 安裝步驟

```bash
# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate

# 安裝相依套件
pip install -e .[dev]

# 啟動 Weaviate 資料庫 (需先填入 OpenAI API Key)
cd docker
OPENAI_APIKEY=你的API金鑰 docker compose up -d

# 匯入資料至資料庫
python scripts/ingest/ingest_reference.py --config cfg.ini

# 啟動 API 服務
uvicorn esun_finrag.api:app --reload

# 產生答案檔案
python scripts/run_predict.py
```

### 設定檔

請將 `cfg_example.ini` 複製成 `cfg.ini` 並填寫以下參數：

- OpenAI API 金鑰 (`openai.api_key`)
- Voyage AI API 金鑰 (`voyage.api_key`)

## API 說明

### 請求格式

```json
POST /api/chat
{
  "qid": 1,
  "source": [442, 115, 440],
  "query": "匯款銀行及中間行所收取之相關費用由誰負擔?",
  "category": "insurance"
}
```

### 回應格式

```json
{
  "qid": 1,
  "retrieve": 442
}
```

## 測試與驗證

執行以下指令進行測試：

```bash
pytest tests/
```

## 常見問題

### 使用其他向量資料庫可行嗎？

可以，目前專案使用 Weaviate，若要更換，可參考 `datastore/weaviate_client.py` 封裝，實作新的資料庫連線介面即可。

### 需要調整混合搜尋比例嗎？

由於 Voyage AI Reranker 已進行深度重排序，初步搜尋比例（alpha 值）不顯著影響結果，因此本專案未提供比例調整。

## 貢獻

本專案採用 MIT License，歡迎透過 Issue 或 Pull Request 提供建議與回饋！

