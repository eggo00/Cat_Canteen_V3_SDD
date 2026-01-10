# Quick Start Guide: 可白牌化智慧餐飲訂單系統平台

**Date**: 2026-01-08
**Target Audience**: 開發團隊
**Estimated Setup Time**: 30 分鐘

---

## 📋 前置需求

### 必要工具
- **Python** 3.11+ (`python --version`)
- **UV** (`uv --version` - 套件管理，符合憲法要求)
- **Node.js** 20+ (`node --version`)
- **pnpm** (`pnpm --version`)
- **PostgreSQL** 15+ (本地開發) 或 Docker
- **Git**

### 安裝 UV（如尚未安裝）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安裝 pnpm（如尚未安裝）
```bash
npm install -g pnpm
```

---

## 🚀 快速啟動（3 步驟）

### 步驟 1：Clone 專案並設定環境

```bash
# Clone 專案
git clone <repository-url>
cd Cat_Canteen_V3_SDD

# 檢查當前分支
git branch  # 應該在 001-white-label-ordering 分支
```

### 步驟 2：啟動後端

```bash
cd backend

# 使用 UV 建立虛擬環境並安裝依賴
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r pyproject.toml

# 複製環境變數範例
cp .env.example .env

# 編輯 .env 檔案，設定資料庫連線
# DATABASE_URL=postgresql://user:password@localhost:5432/catcanteen
# JWT_SECRET=your-secret-key-change-this

# 執行資料庫遷移
alembic upgrade head

# 啟動開發伺服器
uvicorn src.api.main:app --reload --port 8000
```

**驗證**: 訪問 http://localhost:8000/docs 查看 API 文件

### 步驟 3：啟動前端

```bash
cd frontend

# 使用 pnpm 安裝依賴
pnpm install

# 複製環境變數範例
cp .env.example .env

# 編輯 .env 檔案
# VITE_API_BASE_URL=http://localhost:8000/v1

# 啟動開發伺服器
pnpm dev
```

**驗證**: 訪問 http://localhost:5173 查看前端介面

---

## 🐳 使用 Docker Compose（推薦）

```bash
# 在專案根目錄執行
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f backend
```

服務將在以下端口啟動：
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **PostgreSQL**: localhost:5432

---

## 🧪 執行測試

### 後端測試
```bash
cd backend
source .venv/bin/activate

# 執行所有測試
pytest

# 執行特定測試
pytest tests/unit/domain/

# 生成覆蓋率報告
pytest --cov=src --cov-report=html
```

### 前端測試
```bash
cd frontend

# 單元測試
pnpm test

# E2E 測試
pnpm test:e2e

# 測試覆蓋率
pnpm test:coverage
```

---

## 📊 填充測試資料

### 建立範例品牌（Cat Claws 貓咪食堂）

```bash
# 使用 Python 腳本或 API 請求
curl -X POST http://localhost:8000/v1/brands \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "name": "貓咪食堂",
    "slug": "cat-claws",
    "logoUrl": "https://example.com/logo.png",
    "themeConfig": {
      "primaryColor": "#FF6B6B",
      "secondaryColor": "#4ECDC4",
      "fontFamily": "Poppins",
      "borderRadius": "0.75rem",
      "styleKeywords": ["cute", "modern"]
    }
  }'
```

### 上傳範例菜單

參考 `backend/tests/fixtures/sample-menu.json`:

```bash
curl -X POST http://localhost:8000/v1/brands/cat-claws/menu \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  --data @backend/tests/fixtures/sample-menu.json
```

---

## 🔑 取得管理員 Token

### 建立初始管理員帳號（首次執行）

```bash
cd backend
python scripts/create_admin.py --email admin@catcanteen.com --password admin123
```

### 登入取得 Token

```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@catcanteen.com",
    "password": "admin123"
  }'
```

回應範例：
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "Bearer",
  "expiresIn": 86400
}
```

---

## 🎨 測試白牌化功能

### 1. 訪問品牌頁面
```
http://localhost:5173/brands/cat-claws
```

### 2. 前端自動載入主題
- 主題色會應用至所有元件
- Logo 顯示在頁首
- 字體和圓角設定生效

### 3. 建立第二個品牌測試切換
重複上述步驟，使用不同的 `slug` 和主題設定，驗證品牌間完全獨立。

---

## 🛠️ 開發工具

### 資料庫管理
```bash
# 使用 psql 連線
psql postgresql://user:password@localhost:5432/catcanteen

# 查看資料表
\dt

# 查看 brands 資料
SELECT * FROM brands;
```

### 程式碼品質檢查

#### 後端
```bash
cd backend

# Linting
ruff check src/

# Formatting
ruff format src/
```

#### 前端
```bash
cd frontend

# Linting
pnpm lint

# Formatting
pnpm format
```

---

## 🔄 常見開發流程

### 新增 API 端點
1. 在 `src/domain/` 定義業務邏輯
2. 在 `src/application/use_cases/` 建立用例
3. 在 `src/api/v1/routes/` 新增路由
4. 在 `src/api/v1/schemas/` 定義 Pydantic Schema
5. 撰寫測試於 `tests/`
6. 更新 API 文件（FastAPI 自動生成）

### 新增前端元件
1. 在 `src/features/{feature}/components/` 建立元件
2. 在 `src/shared/components/` 建立可重用元件
3. 使用 Headless UI 元件為基礎
4. 使用 Tailwind CSS 樣式（支援主題變數）
5. 撰寫測試於 `tests/unit/`

---

## 📦 部署到 Zeabur

### 1. 建立 Zeabur 專案
```bash
# 安裝 Zeabur CLI
npm install -g @zeabur/cli

# 登入
zeabur login

# 建立專案
zeabur create
```

### 2. 部署後端
```bash
cd backend
zeabur deploy
```

### 3. 部署前端
```bash
cd frontend
zeabur deploy
```

### 4. 設定環境變數
在 Zeabur Dashboard 設定：
- `DATABASE_URL`
- `JWT_SECRET`
- `ALLOWED_ORIGINS`
- `VITE_API_BASE_URL`

---

## 🐛 疑難排解

### 問題：UV 安裝依賴失敗
```bash
# 清除快取
uv cache clean

# 重新安裝
uv pip install -r pyproject.toml --reinstall
```

### 問題：資料庫連線錯誤
```bash
# 檢查 PostgreSQL 是否執行
pg_isready

# 檢查 .env 的 DATABASE_URL 設定
cat .env | grep DATABASE_URL
```

### 問題：前端無法連線後端
```bash
# 檢查後端是否執行
curl http://localhost:8000/health

# 檢查 CORS 設定
# 確保 backend/.env 的 ALLOWED_ORIGINS 包含 http://localhost:5173
```

### 問題：主題不生效
```bash
# 檢查瀏覽器開發者工具 Console
# 確認 CSS Variables 是否正確注入
console.log(getComputedStyle(document.documentElement).getPropertyValue('--color-primary'));
```

---

## 📚 相關文件

- [系統架構設計](./plan.md#project-structure)
- [資料模型](./data-model.md)
- [API 契約](./contracts/api-summary.md)
- [技術研究](./research.md)
- [功能規格](./spec.md)

---

## 🆘 需要幫助？

- 查看專案 README.md
- 參考技術研究文件（research.md）
- 檢查 API 文件：http://localhost:8000/docs
- 提出 Issue 或聯絡團隊

---

**Happy Coding! 🎉**
