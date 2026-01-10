# Implementation Plan: 可白牌化智慧餐飲訂單系統平台

**Branch**: `001-white-label-ordering` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-white-label-ordering/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

建立一個可白牌化的智慧餐飲訂單系統平台，核心能力為：透過 JSON 菜單引擎動態生成多品牌訂餐網站，支援完整的訂餐流程、權限管理、營運數據分析，並預留 AI 擴充接口。技術架構採用前後端分離，後端使用 Python + FastAPI + PostgreSQL，前端使用 React + Headless UI + Tailwind CSS，部署於 Zeabur 雲端平台。系統設計遵循 Clean Architecture，確保模組化、可測試性和可維護性。

## Technical Context

**Language/Version**: Python 3.11+（後端）、TypeScript 5.x（前端）
**Primary Dependencies**:
  - 後端：FastAPI 0.109+、SQLAlchemy 2.x、Pydantic 2.x、PyJWT、uvicorn
  - 前端：React 18+、Vite 5.x、Headless UI（或 Radix UI）、Tailwind CSS 3.x、TanStack Query（React Query）、Zustand（狀態管理）
  - 套件管理：UV（Python）、pnpm（Node.js）
**Storage**: PostgreSQL 15+（由 Zeabur 提供）、SQLAlchemy ORM
**Testing**:
  - 後端：pytest、pytest-asyncio、httpx（API 測試）
  - 前端：Vitest、Testing Library、Playwright（E2E）
**Target Platform**: Zeabur 雲端平台（Docker 容器化部署）、支援現代瀏覽器（Chrome、Firefox、Safari、Edge）
**Project Type**: Web application（前後端分離）
**Performance Goals**:
  - API 回應時間：< 200ms（p95）
  - 前端首次載入：< 2 秒
  - 支援每分鐘 100 筆訂單的併發處理
  - Analytics 數據載入：< 2 秒（10,000 筆訂單）
**Constraints**:
  - 前後端完全分離（RESTful API）
  - 無狀態後端（JWT 驗證）
  - 白牌化引擎必須支援動態主題切換，無需重新部署
  - 符合憲法規定的 UV 套件管理和安全規範
**Scale/Scope**:
  - 初期支援 3-5 個品牌同時運作
  - 預估 1,000+ 活躍訂單/日
  - 菜單品項數：每品牌 50-200 項
  - 管理員用戶：10-20 人（跨品牌）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-First Development
- [x] 功能規格已完成（spec.md）
- [x] 包含明確的問題陳述和目標
- [x] 定義詳細需求和驗收標準
- [x] 記錄設計決策和理由
- [x] 定義成功指標

**Status**: PASS - 規格文件完整且已通過品質檢查

### ✅ II. Clear Documentation
- [x] 本計畫文件將產生：
  - research.md（技術研究和決策）
  - data-model.md（資料模型文件）
  - contracts/（API 規格）
  - quickstart.md（快速開始指南）
- [x] 所有 API 端點將包含輸入/輸出契約
- [x] 關鍵元件將有使用範例

**Status**: PASS - 文件結構已規劃

### ✅ III. Test-Driven Development (NON-NEGOTIABLE)
- [x] 測試策略已規劃：
  - 後端：pytest 進行單元測試、整合測試、API 契約測試
  - 前端：Vitest 進行元件測試、Playwright 進行 E2E 測試
- [x] TDD 工作流將在 tasks.md 中明確定義：測試先行 → 實作 → 重構

**Status**: PASS - 測試工具和流程已確定

### ✅ IV. Code Quality & Maintainability
- [x] 採用 Clean Architecture / Hexagonal Architecture
- [x] 單一職責原則：Domain、Application、Infrastructure 分層
- [x] YAGNI：AI 模組僅預留接口，不過度設計
- [x] 程式碼品質工具：
  - 後端：ruff（linting + formatting）
  - 前端：ESLint + Prettier

**Status**: PASS - 架構設計符合簡潔原則

### ✅ V. Security & Data Protection (NON-NEGOTIABLE)
- [x] JWT-based 身份驗證
- [x] RBAC 權限控制（customer / staff / admin）
- [x] 跨品牌資料隔離機制
- [x] 輸入驗證（Pydantic schemas）
- [x] 防護 OWASP Top 10：
  - SQL Injection：SQLAlchemy ORM + parameterized queries
  - XSS：React 自動 escape、Content Security Policy
  - CSRF：SameSite cookies、CORS 設定
- [x] 敏感資訊保護：
  - .env 檔案使用 .gitignore 排除
  - 資料庫密碼使用環境變數
  - JWT secret 使用環境變數

**Status**: PASS - 安全機制完整規劃

### ✅ Package Management (NON-NEGOTIABLE)
- [x] 後端使用 UV 管理 Python 套件
- [x] 依賴項記錄在 pyproject.toml
- [x] 前端使用 pnpm 管理 Node.js 套件（效能優於 npm/yarn）

**Status**: PASS - 符合憲法要求

### 📋 Constitution Check Summary

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-First Development | ✅ PASS | 規格完整 |
| II. Clear Documentation | ✅ PASS | 文件結構已規劃 |
| III. Test-Driven Development | ✅ PASS | TDD 工作流已定義 |
| IV. Code Quality & Maintainability | ✅ PASS | Clean Architecture |
| V. Security & Data Protection | ✅ PASS | 安全機制完整 |
| Package Management | ✅ PASS | UV + pnpm |

**Overall Status**: ✅ **PASSED** - 可以進入 Phase 0 研究階段

## Project Structure

### Documentation (this feature)

```text
specs/001-white-label-ordering/
├── spec.md              # 功能規格（已完成）
├── plan.md              # 本檔案（實作計畫）
├── research.md          # Phase 0 輸出（技術研究）
├── data-model.md        # Phase 1 輸出（資料模型）
├── quickstart.md        # Phase 1 輸出（快速開始指南）
├── contracts/           # Phase 1 輸出（API 契約）
│   ├── openapi.yaml     # OpenAPI 3.0 規格
│   ├── brand.yaml       # 品牌管理 API
│   ├── menu.yaml        # 菜單管理 API
│   ├── order.yaml       # 訂單管理 API
│   ├── auth.yaml        # 身份驗證 API
│   └── analytics.yaml   # 數據分析 API
├── checklists/          # 品質檢查清單
│   └── requirements.md  # 規格品質檢查（已完成）
└── tasks.md             # Phase 2 輸出（/speckit.tasks 產生）
```

### Source Code (repository root)

```text
# 前後端分離架構

backend/
├── src/
│   ├── domain/                    # Domain Layer（業務邏輯核心）
│   │   ├── entities/              # 實體定義
│   │   │   ├── brand.py
│   │   │   ├── menu.py
│   │   │   ├── order.py
│   │   │   └── user.py
│   │   ├── value_objects/         # 值物件
│   │   │   ├── theme_config.py
│   │   │   ├── customization.py
│   │   │   └── order_status.py
│   │   ├── repositories/          # Repository 介面（Port）
│   │   │   ├── brand_repository.py
│   │   │   ├── menu_repository.py
│   │   │   └── order_repository.py
│   │   └── services/              # Domain Services
│   │       ├── menu_engine.py     # 白牌化菜單引擎
│   │       ├── theme_engine.py    # 主題動態生成
│   │       └── order_service.py
│   ├── application/               # Application Layer（用例層）
│   │   ├── use_cases/             # 業務用例
│   │   │   ├── brand/
│   │   │   │   ├── create_brand.py
│   │   │   │   └── update_brand_theme.py
│   │   │   ├── menu/
│   │   │   │   ├── upload_menu.py
│   │   │   │   └── get_menu_by_brand.py
│   │   │   ├── order/
│   │   │   │   ├── create_order.py
│   │   │   │   ├── update_order_status.py
│   │   │   │   └── get_order.py
│   │   │   └── analytics/
│   │   │       ├── get_revenue_stats.py
│   │   │       └── get_top_items.py
│   │   ├── dto/                   # Data Transfer Objects
│   │   │   ├── brand_dto.py
│   │   │   ├── menu_dto.py
│   │   │   └── order_dto.py
│   │   └── interfaces/            # 應用層介面
│   │       ├── auth_service.py
│   │       └── ai_service.py      # AI 模組介面（stub）
│   ├── infrastructure/            # Infrastructure Layer（基礎設施）
│   │   ├── database/              # 資料庫實作
│   │   │   ├── models/            # SQLAlchemy Models
│   │   │   │   ├── brand_model.py
│   │   │   │   ├── menu_model.py
│   │   │   │   ├── order_model.py
│   │   │   │   └── user_model.py
│   │   │   ├── repositories/      # Repository 實作（Adapter）
│   │   │   │   ├── brand_repository_impl.py
│   │   │   │   ├── menu_repository_impl.py
│   │   │   │   └── order_repository_impl.py
│   │   │   └── session.py         # Database Session
│   │   ├── auth/                  # 身份驗證實作
│   │   │   ├── jwt_handler.py
│   │   │   └── password_hasher.py
│   │   ├── ai/                    # AI 模組實作（stub）
│   │   │   └── ai_service_stub.py
│   │   └── config.py              # 設定管理
│   ├── api/                       # API Layer（REST API 入口）
│   │   ├── v1/
│   │   │   ├── routes/
│   │   │   │   ├── brands.py
│   │   │   │   ├── menus.py
│   │   │   │   ├── orders.py
│   │   │   │   ├── auth.py
│   │   │   │   └── analytics.py
│   │   │   ├── schemas/           # Pydantic Schemas（輸入驗證）
│   │   │   │   ├── brand_schemas.py
│   │   │   │   ├── menu_schemas.py
│   │   │   │   └── order_schemas.py
│   │   │   ├── dependencies.py    # FastAPI Dependencies
│   │   │   └── middleware.py      # 中介層（CORS、Auth、Error Handling）
│   │   └── main.py                # FastAPI App 入口
│   └── main.py                    # 應用程式啟動入口
├── tests/
│   ├── unit/                      # 單元測試
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/               # 整合測試
│   │   ├── api/
│   │   └── database/
│   └── conftest.py                # pytest 設定
├── migrations/                    # Alembic 資料庫遷移
│   └── versions/
├── pyproject.toml                 # Python 專案設定（UV）
├── Dockerfile                     # Docker 映像檔
├── .env.example                   # 環境變數範例
└── README.md

frontend/
├── src/
│   ├── features/                  # Feature-based 組織
│   │   ├── brand/                 # 品牌相關功能
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── api/
│   │   ├── menu/                  # 菜單瀏覽
│   │   │   ├── components/
│   │   │   │   ├── MenuList.tsx
│   │   │   │   ├── MenuItem.tsx
│   │   │   │   └── CategoryFilter.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useMenu.ts
│   │   │   └── api/
│   │   │       └── menuApi.ts
│   │   ├── cart/                  # 購物車
│   │   │   ├── components/
│   │   │   │   ├── Cart.tsx
│   │   │   │   └── CartItem.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useCart.ts
│   │   │   └── store/
│   │   │       └── cartStore.ts   # Zustand Store
│   │   ├── order/                 # 訂單管理
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── api/
│   │   ├── analytics/             # 數據分析（Admin Only）
│   │   │   ├── components/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── RevenueChart.tsx
│   │   │   │   └── TopItemsChart.tsx
│   │   │   ├── hooks/
│   │   │   └── api/
│   │   └── auth/                  # 身份驗證
│   │       ├── components/
│   │       ├── hooks/
│   │       └── api/
│   ├── shared/                    # 共用模組
│   │   ├── components/            # 共用元件（基於 Headless UI）
│   │   │   ├── Button.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Dropdown.tsx
│   │   ├── hooks/                 # 共用 Hooks
│   │   │   ├── useTheme.ts        # 動態主題 Hook
│   │   │   └── useAuth.ts
│   │   ├── utils/
│   │   │   ├── api.ts             # API Client（Fetch/Axios）
│   │   │   └── theme.ts           # 主題工具函式
│   │   └── types/                 # TypeScript 型別定義
│   │       ├── brand.ts
│   │       ├── menu.ts
│   │       └── order.ts
│   ├── layouts/                   # 頁面佈局
│   │   ├── CustomerLayout.tsx
│   │   └── AdminLayout.tsx
│   ├── pages/                     # 頁面路由
│   │   ├── HomePage.tsx
│   │   ├── MenuPage.tsx
│   │   ├── CartPage.tsx
│   │   ├── OrderPage.tsx
│   │   ├── AdminDashboard.tsx
│   │   └── AnalyticsPage.tsx
│   ├── theme/                     # Theme Engine（白牌化核心）
│   │   ├── ThemeProvider.tsx      # 動態主題提供者
│   │   ├── themeConfig.ts         # 主題設定邏輯
│   │   └── tailwind-preset.ts    # Tailwind 動態設定
│   ├── App.tsx                    # 應用程式根元件
│   ├── main.tsx                   # 應用程式入口
│   └── router.tsx                 # React Router 設定
├── tests/
│   ├── unit/                      # Vitest 單元測試
│   └── e2e/                       # Playwright E2E 測試
│       ├── customer-flow.spec.ts
│       └── admin-flow.spec.ts
├── public/
│   └── index.html
├── package.json                   # pnpm 套件設定
├── vite.config.ts                 # Vite 建構設定
├── tailwind.config.js             # Tailwind CSS 設定
├── tsconfig.json                  # TypeScript 設定
├── Dockerfile                     # Docker 映像檔
└── README.md

# Docker Compose（開發環境）
docker-compose.yml                 # 本地開發環境設定
├── services:
│   ├── backend（FastAPI）
│   ├── frontend（Vite dev server）
│   └── db（PostgreSQL）

# 根目錄
.gitignore                         # Git 排除規則（已建立）
README.md                          # 專案說明
```

**Structure Decision**:
採用 **Web application 架構（前後端分離）**，原因如下：

1. **後端（Clean Architecture）**：
   - Domain Layer：核心業務邏輯（品牌引擎、菜單引擎、訂單服務），完全獨立於框架
   - Application Layer：用例協調、DTO 轉換，定義應用邊界
   - Infrastructure Layer：資料庫、外部服務實作，可抽換
   - API Layer：RESTful API 暴露，FastAPI 路由和中介層

2. **前端（Feature-based + Atomic Design）**：
   - Features：依業務功能組織（brand、menu、cart、order、analytics），每個 feature 包含元件、hooks、API
   - Shared：共用元件、工具、型別，基於 Headless UI 實作
   - Theme Engine：白牌化核心，動態載入品牌主題並應用至 Tailwind CSS

3. **分離優勢**：
   - 前後端獨立部署和擴展
   - 前端可替換為其他框架（如 Vue）而不影響後端
   - API 可供其他客戶端（如行動應用）使用

## Complexity Tracking

無憲法違反項目，無需填寫本表格。
