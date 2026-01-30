# Cat Canteen - 可白牌化智慧餐飲訂單系統

Cat Canteen 是一套支援多品牌白牌客製化的智慧餐飲訂單平台。餐廳經營者可快速建立專屬品牌的線上點餐系統，搭配 AI 菜單辨識與數據分析，輕鬆管理營運。

## 功能亮點

- **白牌客製化** - 每個品牌可獨立設定 Logo、主題色彩、字型，擁有專屬品牌網址（`/品牌名稱/menu`）
- **AI 菜單辨識** - 上傳菜單照片，Claude Vision AI 自動辨識品項與價格
- **線上點餐** - 顧客瀏覽菜單、加入購物車、填寫資料即可下單
- **即時訂單管理** - 管理員即時查看新訂單，逐步更新訂單狀態（待處理 → 確認 → 製作中 → 完成）
- **數據分析儀表板** - 營收統計、熱門品項排行、尖峰時段分析，支援 CSV 匯出
- **角色權限控管** - 支援 customer / staff / admin / super_admin 四種角色

## 技術架構

| 層級 | 技術 |
|------|------|
| 前端 | React 18 + TypeScript 5 + Vite 5 + Tailwind CSS |
| 狀態管理 | Zustand（購物車、認證）+ React Query（伺服器資料）|
| 後端 | FastAPI + SQLAlchemy 2.0（async）+ Pydantic 2 |
| 資料庫 | PostgreSQL 15 + Alembic（migration）|
| AI | Anthropic Claude Vision API |
| 部署 | Docker / Zeabur |

## 專案結構

```
Cat_Canteen_V3_SDD/
├── backend/
│   ├── src/
│   │   ├── api/              # FastAPI 路由與 Schema
│   │   ├── application/      # Use Cases 與應用服務
│   │   ├── domain/           # 業務實體與領域邏輯
│   │   └── infrastructure/   # 資料庫、認證、AI、快取
│   ├── migrations/           # Alembic 資料庫遷移
│   ├── tests/                # 單元測試與整合測試
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── features/         # 功能模組（order, auth, brand, ai, menu, cart, analytics）
│   │   ├── pages/            # 頁面元件
│   │   ├── shared/           # 共用元件、Hook、工具
│   │   └── theme/            # 主題設定
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## 快速開始

### 方式一：Docker Compose（推薦）

```bash
docker-compose up
```

啟動後：
- 前端：http://localhost:5173
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs

### 方式二：本地開發

**後端**

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -r pyproject.toml
cp .env.example .env  # 編輯環境變數
alembic upgrade head
uvicorn src.api.main:app --reload
```

**前端**

```bash
cd frontend
pnpm install
pnpm dev
```

### 環境變數（後端）

| 變數 | 必填 | 說明 | 範例 |
|------|------|------|------|
| `DATABASE_URL` | 是 | PostgreSQL 連線字串 | `postgresql://user:pass@localhost:5432/catcanteen` |
| `JWT_SECRET` | 是 | JWT 簽名密鑰 | `your-secret-key` |
| `ENVIRONMENT` | 否 | 執行環境 | `development` / `production` |
| `DEBUG` | 否 | 除錯模式 | `true` / `false` |
| `ALLOWED_ORIGINS` | 否 | CORS 白名單（逗號分隔）| `http://localhost:5173` |
| `ANTHROPIC_API_KEY` | 否 | Claude API Key（AI 菜單辨識用）| `sk-ant-...` |

## 使用指南

### 初始化 Demo 資料

```bash
curl -X POST http://localhost:8000/seed
```

建立 Demo 品牌與菜單：
- 品牌：Demo Cafe（`demo-cafe`）
- 分類：飲品（5 項）、輕食（3 項）、甜點（3 項）
- 管理員帳號：`admin@catcanteen.com` / `admin123`

### 顧客點餐流程

1. 進入品牌菜單頁 → `/{brandSlug}/menu`
2. 瀏覽菜單、搜尋品項、查看 AI 推薦
3. 選擇品項加入購物車
4. 前往購物車確認訂單內容
5. 填寫姓名、電話等資訊後送出訂單
6. 自動跳轉至訂單追蹤頁，即時查看訂單狀態

### 管理員操作

1. **登入** → `/login`，使用管理員帳號登入
2. **管理儀表板** → `/{brandSlug}/admin`
3. **訂單管理** → `/{brandSlug}/admin/orders`
   - 篩選訂單狀態（待處理、確認、製作中、完成、取消）
   - 點擊按鈕更新訂單狀態，每 10 秒自動刷新
4. **品牌設定** → `/{brandSlug}/admin/brand`
   - 修改品牌名稱、Logo、描述
   - 自訂主題色彩（主色、副色、強調色、背景色、文字色）
   - 選擇字型，即時預覽效果
5. **AI 菜單上傳** → `/{brandSlug}/admin/menu/upload`
   - 拖曳或選擇菜單照片上傳
   - AI 自動辨識品項名稱、價格、分類
   - 人工確認後儲存至系統
6. **數據分析** → `/{brandSlug}/analytics`
   - 查看營收趨勢、熱門品項、尖峰時段
   - 選擇日期區間，匯出 CSV 報表

## API 文件

後端啟動後（`DEBUG=true`），可透過 Swagger UI 查看完整 API 文件：

```
http://localhost:8000/docs
```

主要 API 端點：

| 模組 | 路徑 | 說明 |
|------|------|------|
| 認證 | `/v1/auth/*` | 登入、註冊、Token 刷新 |
| 品牌 | `/v1/brands/*` | 品牌 CRUD、主題設定 |
| 菜單 | `/v1/brands/{id}/menu/*` | 菜單與分類管理 |
| 訂單 | `/v1/orders/*` | 訂單建立、查詢、狀態更新 |
| 分析 | `/v1/analytics/*` | 營收統計、匯出報表 |
| AI | `/v1/ai/*` | 菜單辨識、推薦、需求預測 |

## 部署（Zeabur）

1. 在 Zeabur 建立專案，新增 PostgreSQL 服務
2. 新增後端服務，連接 Git repo，設定：
   - Branch：`001-white-label-ordering`
   - Root directory：`backend`
   - Port：`8080`
3. 新增前端服務，設定：
   - Root directory：`frontend`
   - Port：`8080`
4. 設定後端環境變數（`DATABASE_URL`、`JWT_SECRET`、`ALLOWED_ORIGINS` 等）
5. 部署完成後執行 `POST /seed` 初始化 Demo 資料
