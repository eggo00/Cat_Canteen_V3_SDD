# Data Model: 可白牌化智慧餐飲訂單系統平台

**Date**: 2026-01-08
**Feature**: 001-white-label-ordering
**Database**: PostgreSQL 15+
**ORM**: SQLAlchemy 2.x

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│     brands      │◄────────│   menu_categories│◄────────│   menu_items    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
         │                                                         │
         │                                                         │
         │                                                         ▼
         │                                                ┌────────────────────┐
         │                                                │ customization      │
         │                                                │ _options           │
         │                                                └────────────────────┘
         │                                                         ▲
         │                                                         │
         ▼                                                         │
┌─────────────────┐         ┌──────────────────┐         ┌───────────────────┐
│     orders      │─────────│   order_items    │─────────┤                   │
└─────────────────┘         └──────────────────┘         └───────────────────┘
         │
         │
         ▼
┌─────────────────┐
│      users      │
└─────────────────┘
```

---

## 實體定義

### 1. brands（品牌）

**Purpose**: 儲存餐廳品牌資訊和白牌化主題設定

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 品牌唯一識別碼 |
| name | VARCHAR(255) | NOT NULL | 品牌名稱（如：貓咪食堂） |
| slug | VARCHAR(255) | NOT NULL, UNIQUE | URL-safe 識別碼（如：cat-claws） |
| logo_url | TEXT | NOT NULL | 品牌 Logo 圖片 URL |
| theme_config | JSONB | NOT NULL | 主題設定（詳見下方 Schema） |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 品牌是否啟用 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 建立時間 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新時間 |

**theme_config JSONB Schema**:
```json
{
  "primaryColor": "#FF6B6B",
  "secondaryColor": "#4ECDC4",
  "fontFamily": "Poppins",
  "borderRadius": "0.75rem",
  "styleKeywords": ["cute", "modern", "playful"]
}
```

**Indexes**:
- `idx_brands_slug` ON `slug` (UNIQUE)
- `idx_brands_active` ON `is_active` WHERE `is_active = TRUE`

**Validation Rules**:
- `slug` 必須為小寫英數字和連字號（regex: `^[a-z0-9-]+$`）
- `theme_config.primaryColor` 和 `secondaryColor` 必須為有效的 HEX 色碼（regex: `^#[0-9A-Fa-f]{6}$`）
- `logo_url` 必須為有效的 HTTPS URL

---

### 2. menu_categories（菜單分類）

**Purpose**: 菜單品項的分類（如主餐、飲料、甜點）

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 分類唯一識別碼 |
| brand_id | UUID | NOT NULL, FOREIGN KEY → brands.id | 所屬品牌 |
| name | VARCHAR(100) | NOT NULL | 分類名稱 |
| display_order | INTEGER | NOT NULL, DEFAULT 0 | 顯示順序（數字越小越前面） |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 建立時間 |

**Indexes**:
- `idx_categories_brand` ON `brand_id`
- `idx_categories_order` ON `brand_id, display_order`

**Unique Constraint**:
- `uq_category_name_per_brand` ON `(brand_id, name)`

---

### 3. menu_items（菜單品項）

**Purpose**: 具體的餐點或商品

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 品項唯一識別碼 |
| category_id | UUID | NOT NULL, FOREIGN KEY → menu_categories.id | 所屬分類 |
| name | VARCHAR(255) | NOT NULL | 品項名稱 |
| description | TEXT | NULL | 品項簡介 |
| price | DECIMAL(10, 2) | NOT NULL, CHECK (price >= 0) | 基礎價格 |
| image_url | TEXT | NULL | 品項圖片 URL |
| is_available | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否可訂購 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 建立時間 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新時間 |

**Indexes**:
- `idx_items_category` ON `category_id`
- `idx_items_available` ON `is_available` WHERE `is_available = TRUE`

**Cascade Deletion**:
- 當 `menu_categories` 刪除時，連帶刪除所有 `menu_items`（ON DELETE CASCADE）

---

### 4. customization_options（客製化選項）

**Purpose**: 品項的可選配置（加料、甜度、溫度等）

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 選項唯一識別碼 |
| menu_item_id | UUID | NOT NULL, FOREIGN KEY → menu_items.id | 所屬品項 |
| option_type | VARCHAR(50) | NOT NULL | 選項類型（topping/sweetness/temperature） |
| name | VARCHAR(100) | NOT NULL | 選項名稱（如：珍珠、半糖、去冰） |
| price_adjustment | DECIMAL(10, 2) | NOT NULL, DEFAULT 0, CHECK (price_adjustment >= 0) | 額外費用 |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否為預設選項 |
| display_order | INTEGER | NOT NULL, DEFAULT 0 | 顯示順序 |

**Indexes**:
- `idx_options_item` ON `menu_item_id`
- `idx_options_type` ON `menu_item_id, option_type`

**Unique Constraint**:
- `uq_option_name_per_item_type` ON `(menu_item_id, option_type, name)`

**Validation Rules**:
- `option_type` 限定值：`topping`, `sweetness`, `temperature`, `size`, `custom`

---

### 5. orders（訂單）

**Purpose**: 顧客的完整訂單

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 訂單唯一識別碼 |
| order_number | VARCHAR(50) | NOT NULL, UNIQUE | 訂單編號（如：CC20260108-0001） |
| brand_id | UUID | NOT NULL, FOREIGN KEY → brands.id | 所屬品牌 |
| customer_name | VARCHAR(255) | NOT NULL | 顧客姓名 |
| customer_phone | VARCHAR(20) | NOT NULL | 顧客電話 |
| total_amount | DECIMAL(10, 2) | NOT NULL, CHECK (total_amount >= 0) | 訂單總金額 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | 訂單狀態 |
| notes | TEXT | NULL | 備註 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 建立時間 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新時間 |
| completed_at | TIMESTAMP | NULL | 完成時間 |

**Indexes**:
- `idx_orders_number` ON `order_number` (UNIQUE)
- `idx_orders_brand` ON `brand_id`
- `idx_orders_status` ON `brand_id, status`
- `idx_orders_created` ON `brand_id, created_at DESC`（Analytics 查詢）

**Status Values**:
- `pending`: 已接單
- `preparing`: 準備中
- `completed`: 已完成
- `cancelled`: 已取消

**Validation Rules**:
- `order_number` 格式：`CC{YYYYMMDD}-{序號}`（regex: `^CC\d{8}-\d{4}$`）
- `customer_phone` 台灣手機號碼格式（regex: `^09\d{8}$`）

**Business Rules**:
- 訂單完成時，自動設定 `completed_at` 為當前時間
- 訂單狀態變更需記錄在 audit log（未來實作）

---

### 6. order_items（訂單明細）

**Purpose**: 訂單中的單一商品項目

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 明細唯一識別碼 |
| order_id | UUID | NOT NULL, FOREIGN KEY → orders.id | 所屬訂單 |
| menu_item_id | UUID | NOT NULL, FOREIGN KEY → menu_items.id | 品項參照 |
| menu_item_name | VARCHAR(255) | NOT NULL | 品項名稱快照（防止菜單更改） |
| quantity | INTEGER | NOT NULL, CHECK (quantity > 0) | 數量 |
| unit_price | DECIMAL(10, 2) | NOT NULL, CHECK (unit_price >= 0) | 單價快照 |
| customizations | JSONB | NULL | 客製化選項快照 |
| subtotal | DECIMAL(10, 2) | NOT NULL, CHECK (subtotal >= 0) | 小計 |

**Indexes**:
- `idx_order_items_order` ON `order_id`

**customizations JSONB Schema**:
```json
{
  "topping": ["珍珠", "椰果"],
  "sweetness": "半糖",
  "temperature": "去冰",
  "additionalCost": 15.00
}
```

**Cascade Deletion**:
- 當 `orders` 刪除時，連帶刪除所有 `order_items`（ON DELETE CASCADE）

**Business Rules**:
- `subtotal` = `(unit_price + customizations.additionalCost) * quantity`
- 品項名稱和價格使用快照，避免菜單變更影響歷史訂單

---

### 7. users（使用者）

**Purpose**: 系統使用者（staff、admin）

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 使用者唯一識別碼 |
| email | VARCHAR(255) | NOT NULL, UNIQUE | 電子郵件（登入帳號） |
| password_hash | VARCHAR(255) | NOT NULL | 密碼雜湊值（bcrypt） |
| role | VARCHAR(20) | NOT NULL | 角色（customer/staff/admin/super_admin） |
| brand_id | UUID | NULL, FOREIGN KEY → brands.id | 所屬品牌（super_admin 為 NULL） |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 帳號是否啟用 |
| last_login_at | TIMESTAMP | NULL | 最後登入時間 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 建立時間 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新時間 |

**Indexes**:
- `idx_users_email` ON `email` (UNIQUE)
- `idx_users_brand` ON `brand_id`
- `idx_users_role` ON `role`

**Role Values**:
- `customer`: 顧客（無需註冊）
- `staff`: 工作人員（可管理訂單狀態）
- `admin`: 品牌管理員（可管理菜單、訂單、查看 Analytics）
- `super_admin`: 平台管理員（可管理所有品牌）

**Validation Rules**:
- `email` 必須為有效的電子郵件格式
- `password_hash` 使用 bcrypt 加密，cost factor = 12
- `brand_id` 在 `role = super_admin` 時必須為 NULL

---

## 資料完整性規則

### Foreign Key Constraints
1. `menu_categories.brand_id` → `brands.id` (ON DELETE CASCADE)
2. `menu_items.category_id` → `menu_categories.id` (ON DELETE CASCADE)
3. `customization_options.menu_item_id` → `menu_items.id` (ON DELETE CASCADE)
4. `orders.brand_id` → `brands.id` (ON DELETE RESTRICT)
5. `order_items.order_id` → `orders.id` (ON DELETE CASCADE)
6. `order_items.menu_item_id` → `menu_items.id` (ON DELETE RESTRICT)
7. `users.brand_id` → `brands.id` (ON DELETE SET NULL)

### Check Constraints
1. 所有價格欄位必須 >= 0
2. `quantity` 必須 > 0
3. `order_number` 必須符合格式規範

### Unique Constraints
1. `brands.slug` 全域唯一
2. `orders.order_number` 全域唯一
3. `users.email` 全域唯一
4. `(brand_id, category_name)` 每品牌內分類名稱唯一

---

## 資料庫遷移策略（Alembic）

### 初始遷移
```bash
# 建立遷移檔案
alembic revision --autogenerate -m "initial schema"

# 執行遷移
alembic upgrade head
```

### 遷移命名規範
- `YYYY-MM-DD-{description}`: 例如 `2026-01-08-add-brands-table`

### 資料填充（Seed Data）
```python
# 範例：建立預設 super admin
INSERT INTO users (id, email, password_hash, role, is_active)
VALUES (
  gen_random_uuid(),
  'admin@catcanteen.com',
  '$2b$12$...',  -- 密碼：admin123（實際環境請更改）
  'super_admin',
  TRUE
);
```

---

## 效能優化建議

### 1. 查詢優化
- Analytics 查詢使用 `created_at` 索引，限制日期範圍
- 菜單載入使用 JOIN 減少 N+1 問題：
  ```sql
  SELECT b.*, mc.*, mi.*, co.*
  FROM brands b
  JOIN menu_categories mc ON mc.brand_id = b.id
  JOIN menu_items mi ON mi.category_id = mc.id
  LEFT JOIN customization_options co ON co.menu_item_id = mi.id
  WHERE b.slug = ? AND mi.is_available = TRUE;
  ```

### 2. JSONB 索引
```sql
-- 為主題顏色建立 GIN 索引（如需按顏色搜尋）
CREATE INDEX idx_brands_theme_colors
ON brands USING GIN ((theme_config->'primaryColor'));

-- 為客製化選項建立 GIN 索引
CREATE INDEX idx_order_items_customizations
ON order_items USING GIN (customizations);
```

### 3. Materialized Views（Analytics 優化）
```sql
-- 每日營收摘要（定期更新）
CREATE MATERIALIZED VIEW daily_revenue AS
SELECT
  brand_id,
  DATE(created_at) as date,
  COUNT(*) as order_count,
  SUM(total_amount) as total_revenue
FROM orders
WHERE status IN ('completed', 'preparing')
GROUP BY brand_id, DATE(created_at);

-- 每小時更新
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue;
```

---

## 安全性考量

### 1. Row-Level Security (RLS)
品牌管理員僅能存取自己品牌的資料：
```python
# Application Layer 自動注入過濾條件
def get_orders_by_brand(brand_id: str, user: User):
    if user.role != "super_admin":
        assert user.brand_id == brand_id, "Unauthorized"

    return db.query(Order).filter(Order.brand_id == brand_id).all()
```

### 2. 密碼安全
- 使用 bcrypt，cost factor = 12
- 密碼最小長度：8 字元
- 必須包含大小寫字母和數字

### 3. SQL Injection 防護
- 所有查詢使用 SQLAlchemy ORM 或 parameterized queries
- 禁止字串拼接 SQL

---

## 資料備份策略

### 1. 自動備份（Zeabur）
- 每日自動備份
- 保留 30 天

### 2. 災難恢復
- RTO (Recovery Time Objective): < 4 小時
- RPO (Recovery Point Objective): < 24 小時

---

## 未來擴展

### 潛在新增表格
1. **order_status_history**：訂單狀態變更歷史（Audit Log）
2. **user_preferences**：使用者偏好設定（為 AI 推薦做準備）
3. **promotions**：促銷活動和優惠券（未來版本）
4. **delivery_addresses**：外送地址（如整合外送功能）

---

## 總結

此資料模型設計滿足：
- ✅ 白牌化需求（brands.theme_config JSONB）
- ✅ 品牌資料隔離（brand_id 外鍵）
- ✅ 訂單完整性（快照設計）
- ✅ 效能優化（索引策略）
- ✅ 安全性（RLS、密碼加密）
- ✅ 可擴展性（JSONB 彈性欄位）

**Next**: 生成 API Contracts（OpenAPI 3.0 規格）。
