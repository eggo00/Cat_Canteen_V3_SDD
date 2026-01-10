# Technical Research: 可白牌化智慧餐飲訂單系統平台

**Date**: 2026-01-08
**Feature**: 001-white-label-ordering
**Purpose**: 技術選型決策、最佳實踐研究、架構設計理由

---

## 核心技術決策

### 1. 前端框架：React + Headless UI + Tailwind CSS

**Decision**: 採用 React 18+ 作為前端框架，搭配 Headless UI（或 Radix UI）和 Tailwind CSS

**Rationale**:
- **白牌化需求**：本系統的核心是支援多品牌動態主題切換。傳統 UI 框架（如 Ant Design、Material-UI）的風格綁定過重，難以實現真正的品牌獨立性
- **Headless UI 優勢**：
  - 提供無樣式的可存取元件（Accessibility-first）
  - 完全控制視覺呈現，不受框架預設風格限制
  - 確保互動行為一致性（鍵盤導航、ARIA 屬性）
- **Tailwind CSS 優勢**：
  - 支援 Theme Token 和 CSS Variables，可動態注入品牌主題
  - 實現 data-driven UI：從後端接收品牌設定 → 生成 CSS Variables → Tailwind 自動套用
  - 高度可客製化，避免樣式覆蓋的複雜性
- **React 生態成熟**：
  - TanStack Query（React Query）處理伺服器狀態
  - Zustand 管理客戶端狀態（購物車、主題設定）
  - React Router 處理路由
  - 豐富的測試工具（Vitest、Testing Library、Playwright）

**Alternatives Considered**:
- **Vue 3 + Element Plus**：學習曲線平緩，但 Element Plus 風格綁定問題與 Ant Design 類似，不適合白牌化
- **Next.js SSR**：增加複雜度，本專案為 SPA，SSR 對 SEO 需求不高（主要為內部訂餐系統）
- **Svelte + SvelteKit**：生態系統相對較小，團隊學習成本高

**Trade-offs**:
- Headless UI 需要自行實作所有視覺樣式，開發初期成本較高
- Tailwind CSS 的 utility-first 風格可能導致 HTML 類別過多，需要良好的元件抽象

---

### 2. 後端架構：Clean Architecture (Hexagonal Architecture)

**Decision**: 採用 Clean Architecture（又稱 Hexagonal Architecture 或 Ports & Adapters）

**Rationale**:
- **Domain-Driven Design 對齊**：白牌化菜單引擎、主題引擎等核心業務邏輯應獨立於框架和基礎設施
- **可測試性**：Domain Layer 完全不依賴外部框架，可獨立進行單元測試
- **可維護性**：清晰的分層邊界（Domain → Application → Infrastructure → API），降低耦合度
- **未來擴充性**：
  - AI 模組介面預留在 Application Layer，未來可輕鬆替換實作
  - Repository 介面在 Domain Layer，可從 PostgreSQL 切換到其他資料庫（如 MongoDB）而不影響業務邏輯
- **符合憲法原則**：單一職責、可測試性、模組化

**Layers**:
1. **Domain Layer**（核心）：
   - Entities（品牌、菜單、訂單實體）
   - Value Objects（主題設定、客製化選項、訂單狀態）
   - Repository Interfaces（Port）
   - Domain Services（菜單引擎、主題引擎）
2. **Application Layer**（用例）：
   - Use Cases（建立訂單、上傳菜單、更新品牌主題）
   - DTO（數據傳輸物件）
   - Application Interfaces（Auth Service、AI Service）
3. **Infrastructure Layer**（基礎設施）：
   - Database（SQLAlchemy Models、Repository 實作）
   - Auth（JWT Handler、Password Hasher）
   - AI（Stub Implementation）
4. **API Layer**（入口）：
   - FastAPI Routes
   - Pydantic Schemas（輸入驗證）
   - Middleware（CORS、Auth、Error Handling）

**Alternatives Considered**:
- **Simple MVC**：適合小型專案，但隨著白牌化邏輯增加，容易混亂
- **Microservices**：過度設計，初期單體應用更適合快速迭代
- **Django ORM-first**：Django 的 ORM 與業務邏輯綁定過緊，不符合 Clean Architecture 原則

**Trade-offs**:
- 初期需要建立較多的抽象層和介面，開發成本較高
- 小型功能可能感覺"過度工程化"，但長期維護性佳

---

### 3. 白牌化主題引擎設計

**Decision**: 使用 JSON Schema 定義品牌主題，後端驗證並儲存，前端動態載入並應用至 Tailwind CSS

**Implementation Strategy**:

#### 後端（Theme Engine）:
```python
# src/domain/value_objects/theme_config.py
from pydantic import BaseModel, Field

class ThemeConfig(BaseModel):
    primary_color: str = Field(..., regex="^#[0-9A-Fa-f]{6}$")  # 主色
    secondary_color: str = Field(..., regex="^#[0-9A-Fa-f]{6}$")  # 輔色
    logo_url: str = Field(..., pattern="^https?://")
    font_family: str = "Inter"  # 字體（Google Fonts）
    border_radius: str = "0.5rem"  # 圓角
    style_keywords: list[str] = ["modern", "clean"]  # 風格關鍵字

class Brand(BaseModel):
    name: str
    slug: str  # URL-friendly 識別碼
    theme: ThemeConfig
    # ... 其他欄位
```

#### 前端（Theme Provider）:
```typescript
// src/theme/ThemeProvider.tsx
import { useEffect } from 'react';
import { useBrandTheme } from '../features/brand/hooks/useBrandTheme';

export const ThemeProvider = ({ children, brandSlug }) => {
  const { data: theme } = useBrandTheme(brandSlug);

  useEffect(() => {
    if (theme) {
      // 動態注入 CSS Variables
      document.documentElement.style.setProperty('--color-primary', theme.primaryColor);
      document.documentElement.style.setProperty('--color-secondary', theme.secondaryColor);
      document.documentElement.style.setProperty('--font-family', theme.fontFamily);
      document.documentElement.style.setProperty('--border-radius', theme.borderRadius);
    }
  }, [theme]);

  return <div className="theme-container">{children}</div>;
};
```

#### Tailwind 設定:
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
      },
      fontFamily: {
        brand: 'var(--font-family)',
      },
      borderRadius: {
        brand: 'var(--border-radius)',
      },
    },
  },
};
```

**Rationale**:
- CSS Variables 允許運行時動態更新，無需重新編譯 CSS
- Pydantic 確保主題設定格式正確（顏色代碼、URL 格式）
- React Context + Custom Hook 統一管理主題載入邏輯
- Tailwind 的 JIT 模式支援動態 class，但透過 CSS Variables 更簡單

**Alternatives Considered**:
- **Runtime CSS-in-JS**（如 Emotion、Styled Components）：效能較差，且與 Tailwind 的 utility-first 哲學衝突
- **靜態主題檔案**：需要為每個品牌預先生成 CSS，無法動態切換

---

### 4. 資料庫設計策略

**Decision**: 使用 PostgreSQL + SQLAlchemy 2.x，採用單一資料庫多租戶設計（品牌資料隔離）

**Multi-Tenancy Strategy**:
- **Row-Level Security (RLS)**：每筆 Order、MenuItem 紀錄都包含 `brand_id` 外鍵
- **Repository Pattern**：所有查詢自動加上品牌過濾條件
- **JWT Claims**：使用者 token 包含 `brand_id`，API 層自動注入查詢條件

**Schema Highlights**:
- **brands** 表：儲存品牌資訊和主題設定（JSONB 欄位）
- **menu_items** 表：品項資料，關聯至 brand_id 和 category_id
- **customization_options** 表：客製化選項（加料、甜度、溫度），關聯至 menu_item_id
- **orders** 表：訂單主表，包含 brand_id、顧客資訊、總金額、狀態
- **order_items** 表：訂單明細，關聯至 order_id 和 menu_item_id，包含客製化選項（JSONB）
- **users** 表：系統使用者，包含角色（customer / staff / admin）和所屬品牌

**Indexing Strategy**:
- `brand_id` 欄位建立索引（高頻查詢）
- `orders.created_at` 建立索引（Analytics 時間範圍查詢）
- `orders.order_number` 建立唯一索引（訂單編號查詢）

**Alternatives Considered**:
- **每品牌獨立資料庫**：管理複雜度高，不適合初期規模
- **MongoDB**：JSON Schema 靈活性高，但 PostgreSQL 的 JSONB + 關聯式資料混合使用更適合本專案

**Trade-offs**:
- RLS 查詢需要正確實作，否則可能有資料洩漏風險（需完整測試）
- JSONB 欄位（主題設定、客製化選項）需要適當的索引策略以維持查詢效能

---

### 5. 身份驗證與權限控制

**Decision**: JWT-based Authentication + Role-Based Access Control (RBAC)

**Implementation**:

#### JWT Payload:
```json
{
  "sub": "user_id",
  "role": "admin",
  "brand_id": "brand_slug",
  "exp": 1704700800
}
```

#### 權限矩陣:

| 角色 | 菜單瀏覽 | 送出訂單 | 管理訂單狀態 | 上傳菜單 | Analytics |
|------|---------|---------|-------------|---------|-----------|
| **customer** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **staff** | ✅ | ✅ | ✅（限自家品牌） | ❌ | ❌ |
| **admin** | ✅ | ✅ | ✅（限自家品牌） | ✅（限自家品牌） | ✅（限自家品牌） |
| **super_admin** | ✅ | ✅ | ✅（所有品牌） | ✅（所有品牌） | ✅（所有品牌） |

#### FastAPI Dependency:
```python
# src/api/v1/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

async def require_role(required_role: str):
    def dependency(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        payload = decode_jwt(credentials.credentials)
        if payload["role"] not in allowed_roles(required_role):
            raise HTTPException(status_code=403, detail="Permission denied")
        return payload
    return dependency

# 使用範例
@router.post("/brands")
async def create_brand(user=Depends(require_role("admin"))):
    ...
```

**Rationale**:
- JWT 無狀態，適合 RESTful API
- RBAC 模型簡單清晰，符合需求
- FastAPI Dependency Injection 讓權限檢查可重用

**Alternatives Considered**:
- **Session-based Auth**：需要後端狀態管理（Redis），增加複雜度
- **OAuth2 / OIDC**：初期無需第三方登入，過度設計

**Security Considerations**:
- JWT Secret 必須使用環境變數（符合憲法）
- Token 有效期設定為 24 小時（平衡安全性與使用體驗）
- Refresh Token 機制（未來版本）
- HTTPS Only（Zeabur 自動提供）

---

### 6. AI 模組介面設計（Stub Implementation）

**Decision**: 定義標準化 AI Service 介面，目前提供 stub 實作，未來可替換為真實 ML 模型

**Interface Definition**:
```python
# src/application/interfaces/ai_service.py
from abc import ABC, abstractmethod
from typing import List

class AIServicePort(ABC):
    @abstractmethod
    async def recommend_items(
        self,
        brand_id: str,
        user_history: List[str],
        limit: int = 3
    ) -> List[dict]:
        """推薦菜單品項

        Args:
            brand_id: 品牌識別碼
            user_history: 使用者歷史訂單品項 ID 列表
            limit: 推薦數量

        Returns:
            推薦品項列表，格式：[{item_id, name, reason}, ...]
        """
        pass

    @abstractmethod
    async def predict_demand(
        self,
        brand_id: str,
        date_range: tuple
    ) -> dict:
        """預測需求量

        Args:
            brand_id: 品牌識別碼
            date_range: (start_date, end_date)

        Returns:
            預測結果，格式：{date: predicted_orders, ...}
        """
        pass
```

**Stub Implementation**:
```python
# src/infrastructure/ai/ai_service_stub.py
class AIServiceStub(AIServicePort):
    async def recommend_items(self, brand_id, user_history, limit=3):
        # 回傳模擬資料
        return [
            {"item_id": "item_1", "name": "珍珠奶茶", "reason": "熱銷商品"},
            {"item_id": "item_2", "name": "雞排", "reason": "常與奶茶搭配"},
            {"item_id": "item_3", "name": "薯條", "reason": "本週推薦"},
        ][:limit]

    async def predict_demand(self, brand_id, date_range):
        # 回傳簡單預測（使用歷史平均）
        return {"2026-01-09": 120, "2026-01-10": 135}
```

**Rationale**:
- 介面先行設計，確保未來整合時前端和業務邏輯無需修改
- Stub 實作提供固定回應，方便前端開發和測試
- 符合 YAGNI 原則：不過度投資尚未需要的 AI 功能

**Future Integration Path**:
1. 訓練 ML 模型（如協同過濾推薦、時間序列預測）
2. 建立 `AIServiceML` 實作類別
3. 在依賴注入設定中替換 Stub → ML
4. 前端和業務邏輯完全不變

---

### 7. 測試策略

**Decision**: 採用測試金字塔策略：單元測試（70%）、整合測試（20%）、E2E 測試（10%）

**測試工具選擇**:

#### 後端:
- **pytest**：Python 標準測試框架
- **pytest-asyncio**：支援非同步測試
- **httpx**：FastAPI 測試客戶端
- **faker**：生成測試數據
- **coverage.py**：程式碼覆蓋率（目標 80%）

#### 前端:
- **Vitest**：Vite 原生測試框架，速度快於 Jest
- **Testing Library**：元件測試，專注使用者行為
- **MSW (Mock Service Worker)**：API Mocking
- **Playwright**：E2E 測試，支援多瀏覽器

**TDD Workflow**（憲法要求）:
1. 撰寫失敗的測試（根據規格）
2. 實作最小可行程式碼使測試通過
3. 重構程式碼（保持測試綠燈）
4. 重複循環

**測試範例**:
```python
# tests/unit/domain/services/test_menu_engine.py
import pytest
from src.domain.services.menu_engine import MenuEngine

def test_menu_engine_validates_json_schema():
    engine = MenuEngine()
    invalid_menu = {"brand": "Test"}  # 缺少必要欄位

    with pytest.raises(ValidationError):
        engine.validate_menu(invalid_menu)

def test_menu_engine_generates_brand_slug():
    engine = MenuEngine()
    slug = engine.generate_slug("貓咪食堂 Cat Claws")

    assert slug == "cat-claws"
    assert slug.isascii()  # 確保 URL-safe
```

**Rationale**:
- 單元測試覆蓋 Domain Layer，確保業務邏輯正確
- 整合測試驗證 API 端點和資料庫互動
- E2E 測試驗證核心使用者旅程（訂餐流程、白牌化切換）

---

### 8. 部署策略（Zeabur）

**Decision**: 使用 Docker 容器化部署至 Zeabur，前後端分開部署

**Docker Configuration**:

#### 後端 Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv && uv pip install --system -r pyproject.toml
COPY ./src ./src
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

**Zeabur Services**:
- **backend**：FastAPI 服務（Port 8000）
- **frontend**：Nginx 靜態檔案服務（Port 80）
- **database**：PostgreSQL 15（Zeabur Managed）

**Environment Variables** (.env.example):
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.zeabur.app

# Frontend API Endpoint
VITE_API_BASE_URL=https://your-backend-domain.zeabur.app
```

**Rationale**:
- Docker 確保開發和生產環境一致性
- Zeabur 自動處理 HTTPS、負載平衡、自動擴展
- PostgreSQL Managed Service 減少維護負擔

**Trade-offs**:
- Zeabur 鎖定（Vendor Lock-in），但可透過 Docker 遷移到其他平台（如 Railway、Fly.io）
- 初期不需要 Kubernetes 等複雜編排工具

---

## 技術風險評估

| 風險 | 影響 | 機率 | 緩解策略 |
|------|------|------|---------|
| Tailwind CSS 動態主題效能問題 | 中 | 低 | 使用 CSS Variables 而非動態生成 class，預先載入主題 |
| PostgreSQL JSONB 查詢效能 | 中 | 中 | 建立 GIN 索引於 JSONB 欄位，限制 Analytics 查詢範圍 |
| JWT Token 洩漏 | 高 | 低 | HTTPS Only、Token 有效期限制、敏感操作需 Re-authentication |
| 品牌資料隔離失效 | 高 | 低 | 完整的整合測試覆蓋權限檢查、Code Review 檢查所有查詢 |
| Zeabur 服務中斷 | 中 | 低 | 準備 Docker Compose 設定，可快速遷移到其他平台 |

---

## 總結

本研究文件確立了可白牌化智慧餐飲訂單系統的技術基礎：

1. ✅ **前端**：React + Headless UI + Tailwind CSS，支援動態主題切換
2. ✅ **後端**：Clean Architecture + FastAPI + PostgreSQL，確保模組化和可測試性
3. ✅ **白牌化引擎**：JSON Schema 定義主題，CSS Variables 動態注入
4. ✅ **安全性**：JWT + RBAC，品牌資料隔離
5. ✅ **AI 預留**：介面先行，Stub 實作
6. ✅ **測試**：TDD 工作流，測試金字塔策略
7. ✅ **部署**：Docker + Zeabur，自動化 CI/CD

**Next Steps**: 進入 Phase 1，生成 data-model.md 和 API contracts。
