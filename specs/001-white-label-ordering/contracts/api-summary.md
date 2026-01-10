# API Contracts Summary: 可白牌化智慧餐飲訂單系統

**Date**: 2026-01-08
**API Version**: v1
**Base URL**: `https://api.catcanteen.app/v1`
**Authentication**: JWT Bearer Token

---

## API 端點總覽

### 品牌管理 API (Brands)
- `POST /brands` - 建立新品牌（admin/super_admin）
- `GET /brands/{slug}` - 取得品牌詳情（含主題設定）
- `PUT /brands/{slug}/theme` - 更新品牌主題（admin/super_admin）
- `GET /brands` - 列出所有品牌（super_admin only）

### 菜單管理 API (Menus)
- `POST /brands/{slug}/menu` - 上傳完整菜單 JSON（admin）
- `GET /brands/{slug}/menu` - 取得品牌菜單（公開）
- `GET /brands/{slug}/menu/items/{itemId}` - 取得品項詳情（公開）
- `PUT /menu/items/{itemId}` - 更新品項（admin）
- `PATCH /menu/items/{itemId}/availability` - 切換品項可用性（staff/admin）

### 訂單管理 API (Orders)
- `POST /brands/{slug}/orders` - 建立訂單（公開）
- `GET /orders/{orderNumber}` - 查詢訂單狀態（公開）
- `PUT /orders/{orderNumber}/status` - 更新訂單狀態（staff/admin）
- `GET /brands/{slug}/orders` - 取得品牌訂單列表（staff/admin）

### 身份驗證 API (Auth)
- `POST /auth/login` - 使用者登入
- `POST /auth/refresh` - 刷新 Token
- `POST /auth/logout` - 使用者登出

### 數據分析 API (Analytics)
- `GET /brands/{slug}/analytics/revenue` - 營收統計（admin）
- `GET /brands/{slug}/analytics/top-items` - 熱銷品項（admin）
- `GET /brands/{slug}/analytics/orders-by-hour` - 時段分析（admin）

### AI 推薦 API (AI - Stub)
- `GET /brands/{slug}/recommendations` - 取得推薦品項（公開）

---

## 核心 Schema 定義

### BrandTheme
```json
{
  "primaryColor": "#FF6B6B",
  "secondaryColor": "#4ECDC4",
  "fontFamily": "Poppins",
  "borderRadius": "0.75rem",
  "styleKeywords": ["cute", "modern"]
}
```

### MenuItem
```json
{
  "id": "uuid",
  "name": "珍珠奶茶",
  "description": "經典台灣珍珠奶茶",
  "price": 50.00,
  "imageUrl": "https://...",
  "category": {
    "id": "uuid",
    "name": "飲料"
  },
  "customizationOptions": [
    {
      "type": "topping",
      "name": "珍珠",
      "priceAdjustment": 10.00
    },
    {
      "type": "sweetness",
      "name": "半糖",
      "priceAdjustment": 0
    }
  ],
  "isAvailable": true
}
```

### Order
```json
{
  "orderNumber": "CC20260108-0001",
  "brandSlug": "cat-claws",
  "customerName": "王小明",
  "customerPhone": "0912345678",
  "items": [
    {
      "menuItemId": "uuid",
      "menuItemName": "珍珠奶茶",
      "quantity": 2,
      "unitPrice": 50.00,
      "customizations": {
        "topping": ["珍珠"],
        "sweetness": "半糖",
        "temperature": "去冰",
        "additionalCost": 10.00
      },
      "subtotal": 120.00
    }
  ],
  "totalAmount": 120.00,
  "status": "pending",
  "notes": "不要吸管",
  "createdAt": "2026-01-08T10:30:00Z"
}
```

---

## 權限矩陣

| Endpoint | customer | staff | admin | super_admin |
|----------|----------|-------|-------|-------------|
| GET /brands/{slug} | ✅ | ✅ | ✅ | ✅ |
| POST /brands | ❌ | ❌ | ✅ | ✅ |
| GET /brands/{slug}/menu | ✅ | ✅ | ✅ | ✅ |
| POST /brands/{slug}/menu | ❌ | ❌ | ✅（限自家） | ✅ |
| POST /brands/{slug}/orders | ✅ | ✅ | ✅ | ✅ |
| GET /orders/{orderNumber} | ✅ | ✅ | ✅ | ✅ |
| PUT /orders/{orderNumber}/status | ❌ | ✅（限自家） | ✅（限自家） | ✅ |
| GET /brands/{slug}/analytics/* | ❌ | ❌ | ✅（限自家） | ✅ |

---

## 錯誤回應格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid menu JSON format",
    "details": [
      {
        "field": "theme.primaryColor",
        "issue": "Invalid HEX color code"
      }
    ]
  }
}
```

**Error Codes**:
- `VALIDATION_ERROR`: 輸入驗證失敗
- `UNAUTHORIZED`: 未登入或 Token 無效
- `FORBIDDEN`: 權限不足
- `NOT_FOUND`: 資源不存在
- `CONFLICT`: 資料衝突（如 slug 重複）
- `INTERNAL_ERROR`: 伺服器錯誤

---

## 速率限制

- 公開端點：100 requests / minute / IP
- 已驗證端點：1000 requests / minute / user
- 菜單上傳：10 requests / hour / admin

---

## CORS 設定

```yaml
Allowed Origins:
  - https://*.zeabur.app
  - http://localhost:5173 (dev only)
Allowed Methods: GET, POST, PUT, PATCH, DELETE
Allowed Headers: Authorization, Content-Type
Max Age: 86400
```

---

**Note**: 完整的 OpenAPI 3.0 規格將在實作階段詳細定義。本文件提供核心端點和資料結構概覽。
