# Tasks: 可白牌化智慧餐飲訂單系統平台

**Feature**: 001-white-label-ordering
**Input**: Design documents from `/specs/001-white-label-ordering/`
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/api-summary.md, quickstart.md

**TDD Workflow**: All tasks follow Test-Driven Development - write tests first, ensure they fail, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- **Tests**: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Create backend directory structure: backend/src/{domain,application,infrastructure,api}, backend/tests/{unit,integration}
- [ ] T002 [P] Create frontend directory structure: frontend/src/{features,shared,layouts,pages,theme}
- [ ] T003 [P] Initialize Python project with UV: backend/pyproject.toml with FastAPI 0.109+, SQLAlchemy 2.x, Pydantic 2.x, PyJWT, uvicorn, pytest
- [ ] T004 [P] Initialize frontend project with Vite: frontend/package.json with React 18+, Headless UI, Tailwind CSS 3.x, TanStack Query, Zustand, pnpm
- [ ] T005 [P] Configure backend linting: backend/.ruff.toml with ruff configuration
- [ ] T006 [P] Configure frontend linting: frontend/.eslintrc.json and frontend/.prettierrc
- [ ] T007 [P] Create backend Dockerfile with UV and Python 3.11
- [ ] T008 [P] Create frontend Dockerfile with Node 20 and pnpm
- [ ] T009 Create docker-compose.yml with backend, frontend, and PostgreSQL services
- [ ] T010 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, ALLOWED_ORIGINS
- [ ] T011 [P] Create frontend/.env.example with VITE_API_BASE_URL
- [ ] T012 [P] Add .gitignore with .env, .venv, node_modules, dist, __pycache__

**Checkpoint**: Project structure ready for foundational work

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & ORM Setup

- [ ] T013 Setup Alembic migrations framework in backend/migrations/
- [ ] T014 Create initial database schema migration for all 7 entities (brands, menu_categories, menu_items, customization_options, orders, order_items, users)
- [ ] T015 Create SQLAlchemy models in backend/src/infrastructure/database/models/brand_model.py
- [ ] T016 [P] Create SQLAlchemy models in backend/src/infrastructure/database/models/menu_model.py
- [ ] T017 [P] Create SQLAlchemy models in backend/src/infrastructure/database/models/order_model.py
- [ ] T018 [P] Create SQLAlchemy models in backend/src/infrastructure/database/models/user_model.py
- [ ] T019 Create database session management in backend/src/infrastructure/database/session.py
- [ ] T020 Create database initialization script in backend/scripts/init_db.py

### Authentication & Security Infrastructure

- [ ] T021 [P] Implement JWT token handler in backend/src/infrastructure/auth/jwt_handler.py
- [ ] T022 [P] Implement password hasher using bcrypt in backend/src/infrastructure/auth/password_hasher.py
- [ ] T023 Create FastAPI auth dependencies in backend/src/api/v1/dependencies.py (get_current_user, require_role)
- [ ] T024 Create authentication middleware in backend/src/api/v1/middleware.py (CORS, error handling)

### API Infrastructure

- [ ] T025 Create FastAPI main app in backend/src/api/main.py with CORS and middleware setup
- [ ] T026 Create API router structure in backend/src/api/v1/routes/__init__.py
- [ ] T027 Create base Pydantic schemas in backend/src/api/v1/schemas/__init__.py
- [ ] T028 Create error response models in backend/src/api/v1/schemas/error_schemas.py

### Configuration & Utilities

- [ ] T029 [P] Create configuration management in backend/src/infrastructure/config.py
- [ ] T030 [P] Create admin user creation script in backend/scripts/create_admin.py

### Frontend Core Infrastructure

- [ ] T031 Setup React Router in frontend/src/router.tsx with CustomerLayout and AdminLayout routes
- [ ] T032 Create API client with axios in frontend/src/shared/utils/api.ts
- [ ] T033 Setup TanStack Query provider in frontend/src/App.tsx
- [ ] T034 Create auth context in frontend/src/shared/hooks/useAuth.ts
- [ ] T035 [P] Create base TypeScript types in frontend/src/shared/types/brand.ts
- [ ] T036 [P] Create base TypeScript types in frontend/src/shared/types/menu.ts
- [ ] T037 [P] Create base TypeScript types in frontend/src/shared/types/order.ts
- [ ] T038 Setup Tailwind CSS configuration with theme variables in frontend/tailwind.config.js

### Testing Infrastructure

- [ ] T039 [P] Setup pytest configuration in backend/tests/conftest.py with test database fixtures
- [ ] T040 [P] Setup Vitest configuration in frontend/vite.config.ts
- [ ] T041 [P] Setup Playwright configuration in frontend/playwright.config.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 品牌快速上線（白牌化核心）(Priority: P1) 🎯 MVP

**Goal**: 管理員能為新餐廳品牌快速建立訂餐系統，上傳菜單資料、設定品牌視覺風格，前端立即呈現該品牌獨特介面

**Independent Test**: 上傳一個全新品牌的 JSON 菜單檔案，系統應立即生成該品牌的訂餐網站，前端正確顯示品牌 Logo、主題色、菜單項目

### Backend Tests for User Story 1 (Write First - TDD) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T042 [P] [US1] Contract test for POST /brands endpoint in backend/tests/integration/api/test_brands_api.py
- [ ] T043 [P] [US1] Contract test for GET /brands/{slug} endpoint in backend/tests/integration/api/test_brands_api.py
- [ ] T044 [P] [US1] Contract test for PUT /brands/{slug}/theme endpoint in backend/tests/integration/api/test_brands_api.py
- [ ] T045 [P] [US1] Contract test for POST /brands/{slug}/menu endpoint in backend/tests/integration/api/test_menu_api.py
- [ ] T046 [P] [US1] Contract test for GET /brands/{slug}/menu endpoint in backend/tests/integration/api/test_menu_api.py
- [ ] T047 [P] [US1] Unit test for Brand entity validation in backend/tests/unit/domain/entities/test_brand.py
- [ ] T048 [P] [US1] Unit test for ThemeConfig value object in backend/tests/unit/domain/value_objects/test_theme_config.py
- [ ] T049 [P] [US1] Unit test for MenuEngine service in backend/tests/unit/domain/services/test_menu_engine.py
- [ ] T050 [P] [US1] Unit test for ThemeEngine service in backend/tests/unit/domain/services/test_theme_engine.py
- [ ] T051 [P] [US1] Integration test for brand creation workflow in backend/tests/integration/test_brand_workflow.py
- [ ] T052 [P] [US1] Integration test for menu upload workflow in backend/tests/integration/test_menu_workflow.py

### Backend Domain Layer for User Story 1

- [ ] T053 [P] [US1] Create Brand entity in backend/src/domain/entities/brand.py with validation
- [ ] T054 [P] [US1] Create Category entity in backend/src/domain/entities/category.py
- [ ] T055 [P] [US1] Create MenuItem entity in backend/src/domain/entities/menu_item.py
- [ ] T056 [P] [US1] Create CustomizationOption entity in backend/src/domain/entities/customization_option.py
- [ ] T057 [P] [US1] Create ThemeConfig value object in backend/src/domain/value_objects/theme_config.py with HEX color validation
- [ ] T058 [P] [US1] Create BrandRepository interface in backend/src/domain/repositories/brand_repository.py
- [ ] T059 [P] [US1] Create MenuRepository interface in backend/src/domain/repositories/menu_repository.py
- [ ] T060 [US1] Create MenuEngine domain service in backend/src/domain/services/menu_engine.py (JSON validation, slug generation)
- [ ] T061 [US1] Create ThemeEngine domain service in backend/src/domain/services/theme_engine.py (theme validation, color contrast check)

### Backend Application Layer for User Story 1

- [ ] T062 [P] [US1] Create BrandDTO in backend/src/application/dto/brand_dto.py
- [ ] T063 [P] [US1] Create MenuDTO in backend/src/application/dto/menu_dto.py
- [ ] T064 [US1] Create CreateBrand use case in backend/src/application/use_cases/brand/create_brand.py
- [ ] T065 [US1] Create GetBrandBySlug use case in backend/src/application/use_cases/brand/get_brand.py
- [ ] T066 [US1] Create UpdateBrandTheme use case in backend/src/application/use_cases/brand/update_brand_theme.py
- [ ] T067 [US1] Create UploadMenu use case in backend/src/application/use_cases/menu/upload_menu.py
- [ ] T068 [US1] Create GetMenuByBrand use case in backend/src/application/use_cases/menu/get_menu_by_brand.py

### Backend Infrastructure Layer for User Story 1

- [ ] T069 [US1] Implement BrandRepository in backend/src/infrastructure/database/repositories/brand_repository_impl.py
- [ ] T070 [US1] Implement MenuRepository in backend/src/infrastructure/database/repositories/menu_repository_impl.py

### Backend API Layer for User Story 1

- [ ] T071 [P] [US1] Create brand Pydantic schemas in backend/src/api/v1/schemas/brand_schemas.py (CreateBrandRequest, BrandResponse, UpdateThemeRequest)
- [ ] T072 [P] [US1] Create menu Pydantic schemas in backend/src/api/v1/schemas/menu_schemas.py (UploadMenuRequest, MenuResponse)
- [ ] T073 [US1] Implement brand routes in backend/src/api/v1/routes/brands.py (POST /brands, GET /brands/{slug}, PUT /brands/{slug}/theme)
- [ ] T074 [US1] Implement menu routes in backend/src/api/v1/routes/menus.py (POST /brands/{slug}/menu, GET /brands/{slug}/menu)
- [ ] T075 [US1] Add error handling for menu validation errors with specific field details
- [ ] T076 [US1] Add logging for brand creation and menu upload operations

### Frontend Tests for User Story 1 (Write First - TDD) ⚠️

- [ ] T077 [P] [US1] Unit test for ThemeProvider component in frontend/tests/unit/theme/test_theme_provider.test.tsx
- [ ] T078 [P] [US1] Unit test for useTheme hook in frontend/tests/unit/shared/hooks/test_use_theme.test.ts
- [ ] T079 [P] [US1] Unit test for MenuList component in frontend/tests/unit/features/menu/test_menu_list.test.tsx
- [ ] T080 [P] [US1] E2E test for brand theme switching in frontend/tests/e2e/brand-theme.spec.ts

### Frontend Implementation for User Story 1

- [ ] T081 [US1] Create theme configuration logic in frontend/src/theme/themeConfig.ts (CSS variable injection)
- [ ] T082 [US1] Create ThemeProvider component in frontend/src/theme/ThemeProvider.tsx (dynamic theme loading)
- [ ] T083 [US1] Create useTheme hook in frontend/src/shared/hooks/useTheme.ts
- [ ] T084 [P] [US1] Create brand API client in frontend/src/features/brand/api/brandApi.ts
- [ ] T085 [P] [US1] Create useBrandTheme hook in frontend/src/features/brand/hooks/useBrandTheme.ts
- [ ] T086 [US1] Create menu API client in frontend/src/features/menu/api/menuApi.ts
- [ ] T087 [US1] Create useMenu hook in frontend/src/features/menu/hooks/useMenu.ts
- [ ] T088 [P] [US1] Create MenuList component in frontend/src/features/menu/components/MenuList.tsx
- [ ] T089 [P] [US1] Create MenuItem component in frontend/src/features/menu/components/MenuItem.tsx
- [ ] T090 [P] [US1] Create CategoryFilter component in frontend/src/features/menu/components/CategoryFilter.tsx
- [ ] T091 [US1] Create MenuPage in frontend/src/pages/MenuPage.tsx with ThemeProvider integration
- [ ] T092 [US1] Update App.tsx to include brand slug routing and theme initialization

### Integration & Validation for User Story 1

- [ ] T093 [US1] Run all US1 tests and ensure they pass (backend pytest + frontend vitest)
- [ ] T094 [US1] Create sample menu JSON fixture in backend/tests/fixtures/sample-menu.json
- [ ] T095 [US1] Manual test: Upload sample menu and verify frontend displays correctly with theme
- [ ] T096 [US1] Manual test: Create two brands with different themes and verify isolation

**Checkpoint**: User Story 1 complete - brand onboarding and white-label theme system functional

---

## Phase 4: User Story 2 - 顧客完整訂餐流程 (Priority: P2)

**Goal**: 顧客能瀏覽菜單、選擇餐點並客製化、加入購物車、確認訂單、取得訂單編號並追蹤狀態

**Independent Test**: 新顧客從進入網站到取得訂單編號，整個流程應能在 3 分鐘內完成，每個步驟都有清楚的視覺回饋

### Backend Tests for User Story 2 (Write First - TDD) ⚠️

- [ ] T097 [P] [US2] Contract test for POST /brands/{slug}/orders endpoint in backend/tests/integration/api/test_orders_api.py
- [ ] T098 [P] [US2] Contract test for GET /orders/{orderNumber} endpoint in backend/tests/integration/api/test_orders_api.py
- [ ] T099 [P] [US2] Unit test for Order entity in backend/tests/unit/domain/entities/test_order.py
- [ ] T100 [P] [US2] Unit test for OrderItem entity in backend/tests/unit/domain/entities/test_order_item.py
- [ ] T101 [P] [US2] Unit test for OrderStatus value object in backend/tests/unit/domain/value_objects/test_order_status.py
- [ ] T102 [P] [US2] Unit test for OrderService in backend/tests/unit/domain/services/test_order_service.py
- [ ] T103 [P] [US2] Integration test for complete order flow in backend/tests/integration/test_order_workflow.py

### Backend Domain Layer for User Story 2

- [ ] T104 [P] [US2] Create Order entity in backend/src/domain/entities/order.py with order number generation
- [ ] T105 [P] [US2] Create OrderItem entity in backend/src/domain/entities/order_item.py
- [ ] T106 [P] [US2] Create OrderStatus value object in backend/src/domain/value_objects/order_status.py (pending, preparing, completed, cancelled)
- [ ] T107 [P] [US2] Create OrderRepository interface in backend/src/domain/repositories/order_repository.py
- [ ] T108 [US2] Create OrderService domain service in backend/src/domain/services/order_service.py (order validation, total calculation)

### Backend Application Layer for User Story 2

- [ ] T109 [P] [US2] Create OrderDTO in backend/src/application/dto/order_dto.py
- [ ] T110 [US2] Create CreateOrder use case in backend/src/application/use_cases/order/create_order.py
- [ ] T111 [US2] Create GetOrder use case in backend/src/application/use_cases/order/get_order.py
- [ ] T112 [US2] Create UpdateOrderStatus use case in backend/src/application/use_cases/order/update_order_status.py

### Backend Infrastructure Layer for User Story 2

- [ ] T113 [US2] Implement OrderRepository in backend/src/infrastructure/database/repositories/order_repository_impl.py

### Backend API Layer for User Story 2

- [ ] T114 [P] [US2] Create order Pydantic schemas in backend/src/api/v1/schemas/order_schemas.py (CreateOrderRequest, OrderResponse)
- [ ] T115 [US2] Implement order routes in backend/src/api/v1/routes/orders.py (POST /brands/{slug}/orders, GET /orders/{orderNumber}, PUT /orders/{orderNumber}/status)
- [ ] T116 [US2] Add validation for customer phone format (Taiwan mobile)
- [ ] T117 [US2] Add logging for order creation and status updates

### Frontend Tests for User Story 2 (Write First - TDD) ⚠️

- [ ] T118 [P] [US2] Unit test for Cart component in frontend/tests/unit/features/cart/test_cart.test.tsx
- [ ] T119 [P] [US2] Unit test for cartStore in frontend/tests/unit/features/cart/test_cart_store.test.ts
- [ ] T120 [P] [US2] Unit test for useCart hook in frontend/tests/unit/features/cart/test_use_cart.test.ts
- [ ] T121 [P] [US2] E2E test for complete order flow in frontend/tests/e2e/customer-flow.spec.ts

### Frontend Implementation for User Story 2

- [ ] T122 [US2] Create Zustand cart store in frontend/src/features/cart/store/cartStore.ts (add, remove, update quantity, clear)
- [ ] T123 [US2] Create useCart hook in frontend/src/features/cart/hooks/useCart.ts
- [ ] T124 [P] [US2] Create Cart component in frontend/src/features/cart/components/Cart.tsx
- [ ] T125 [P] [US2] Create CartItem component in frontend/src/features/cart/components/CartItem.tsx
- [ ] T126 [US2] Create order API client in frontend/src/features/order/api/orderApi.ts
- [ ] T127 [US2] Create useCreateOrder hook in frontend/src/features/order/hooks/useCreateOrder.ts
- [ ] T128 [US2] Create useOrderStatus hook in frontend/src/features/order/hooks/useOrderStatus.ts
- [ ] T129 [P] [US2] Create OrderConfirmation component in frontend/src/features/order/components/OrderConfirmation.tsx
- [ ] T130 [P] [US2] Create OrderTracking component in frontend/src/features/order/components/OrderTracking.tsx
- [ ] T131 [US2] Create CartPage in frontend/src/pages/CartPage.tsx
- [ ] T132 [US2] Create OrderPage in frontend/src/pages/OrderPage.tsx (order confirmation and tracking)
- [ ] T133 [US2] Add cart icon with item count to navigation

### Integration & Validation for User Story 2

- [ ] T134 [US2] Run all US2 tests and ensure they pass
- [ ] T135 [US2] Manual test: Complete order flow from menu browsing to order tracking
- [ ] T136 [US2] Manual test: Verify order isolation between different brands

**Checkpoint**: User Story 2 complete - complete customer ordering flow functional

---

## Phase 5: User Story 3 - 管理員營運數據分析 (Priority: P3)

**Goal**: 管理員能查看即時和歷史營運數據，包括營收統計、訂單趨勢、熱銷品項排行、時段分布，並匯出報表

**Independent Test**: 管理員登入後能看到過去 30 天的營收圖表、今日熱銷前 10 名商品、各時段訂單分布，所有數據能在 2 秒內載入

### Backend Tests for User Story 3 (Write First - TDD) ⚠️

- [ ] T137 [P] [US3] Contract test for GET /brands/{slug}/analytics/revenue endpoint in backend/tests/integration/api/test_analytics_api.py
- [ ] T138 [P] [US3] Contract test for GET /brands/{slug}/analytics/top-items endpoint in backend/tests/integration/api/test_analytics_api.py
- [ ] T139 [P] [US3] Contract test for GET /brands/{slug}/analytics/orders-by-hour endpoint in backend/tests/integration/api/test_analytics_api.py
- [ ] T140 [P] [US3] Unit test for analytics calculations in backend/tests/unit/application/use_cases/analytics/test_analytics.py

### Backend Application Layer for User Story 3

- [ ] T141 [P] [US3] Create GetRevenueStats use case in backend/src/application/use_cases/analytics/get_revenue_stats.py
- [ ] T142 [P] [US3] Create GetTopItems use case in backend/src/application/use_cases/analytics/get_top_items.py
- [ ] T143 [P] [US3] Create GetOrdersByHour use case in backend/src/application/use_cases/analytics/get_orders_by_hour.py
- [ ] T144 [P] [US3] Create ExportReport use case in backend/src/application/use_cases/analytics/export_report.py (CSV generation)

### Backend API Layer for User Story 3

- [ ] T145 [P] [US3] Create analytics Pydantic schemas in backend/src/api/v1/schemas/analytics_schemas.py
- [ ] T146 [US3] Implement analytics routes in backend/src/api/v1/routes/analytics.py (revenue, top-items, orders-by-hour endpoints)
- [ ] T147 [US3] Add admin role requirement to all analytics endpoints
- [ ] T148 [US3] Add query optimization for analytics queries (date range filtering, indexing)

### Frontend Tests for User Story 3 (Write First - TDD) ⚠️

- [ ] T149 [P] [US3] Unit test for Dashboard component in frontend/tests/unit/features/analytics/test_dashboard.test.tsx
- [ ] T150 [P] [US3] Unit test for RevenueChart component in frontend/tests/unit/features/analytics/test_revenue_chart.test.tsx

### Frontend Implementation for User Story 3

- [ ] T151 [US3] Create analytics API client in frontend/src/features/analytics/api/analyticsApi.ts
- [ ] T152 [US3] Create useAnalytics hook in frontend/src/features/analytics/hooks/useAnalytics.ts
- [ ] T153 [P] [US3] Create Dashboard component in frontend/src/features/analytics/components/Dashboard.tsx
- [ ] T154 [P] [US3] Create RevenueChart component in frontend/src/features/analytics/components/RevenueChart.tsx (using recharts or similar)
- [ ] T155 [P] [US3] Create TopItemsChart component in frontend/src/features/analytics/components/TopItemsChart.tsx
- [ ] T156 [P] [US3] Create OrdersByHourChart component in frontend/src/features/analytics/components/OrdersByHourChart.tsx
- [ ] T157 [P] [US3] Create DateRangePicker component in frontend/src/shared/components/DateRangePicker.tsx
- [ ] T158 [US3] Create AnalyticsPage in frontend/src/pages/AnalyticsPage.tsx
- [ ] T159 [US3] Add export report button with CSV download functionality

### Integration & Validation for User Story 3

- [ ] T160 [US3] Run all US3 tests and ensure they pass
- [ ] T161 [US3] Manual test: Verify analytics data accuracy with sample orders
- [ ] T162 [US3] Manual test: Verify brand admins can only see their own brand analytics

**Checkpoint**: User Story 3 complete - analytics dashboard functional

---

## Phase 6: User Story 4 - 品牌與權限管理 (Priority: P4)

**Goal**: 平台管理員能建立和管理多個品牌帳號，為每個品牌指派獨立的管理員帳號，確保資料安全和隱私

**Independent Test**: 建立兩個品牌，各自指派一位管理員。Brand A 管理員應只能看到 Brand A 的資料，無法存取 Brand B 的任何資訊

### Backend Tests for User Story 4 (Write First - TDD) ⚠️

- [ ] T163 [P] [US4] Contract test for POST /auth/login endpoint in backend/tests/integration/api/test_auth_api.py
- [ ] T164 [P] [US4] Contract test for brand isolation in backend/tests/integration/test_brand_isolation.py
- [ ] T165 [P] [US4] Unit test for permission checking in backend/tests/unit/domain/services/test_permission_service.py

### Backend Domain Layer for User Story 4

- [ ] T166 [P] [US4] Create User entity in backend/src/domain/entities/user.py
- [ ] T167 [P] [US4] Create UserRepository interface in backend/src/domain/repositories/user_repository.py

### Backend Application Layer for User Story 4

- [ ] T168 [P] [US4] Create AuthService interface in backend/src/application/interfaces/auth_service.py
- [ ] T169 [US4] Create Login use case in backend/src/application/use_cases/auth/login.py
- [ ] T170 [US4] Create RefreshToken use case in backend/src/application/use_cases/auth/refresh_token.py

### Backend Infrastructure Layer for User Story 4

- [ ] T171 [US4] Implement UserRepository in backend/src/infrastructure/database/repositories/user_repository_impl.py
- [ ] T172 [US4] Implement AuthService in backend/src/infrastructure/auth/auth_service_impl.py

### Backend API Layer for User Story 4

- [ ] T173 [P] [US4] Create auth Pydantic schemas in backend/src/api/v1/schemas/auth_schemas.py (LoginRequest, TokenResponse)
- [ ] T174 [US4] Implement auth routes in backend/src/api/v1/routes/auth.py (POST /auth/login, POST /auth/refresh, POST /auth/logout)
- [ ] T175 [US4] Add brand_id validation to all authenticated endpoints (ensure users can only access their brand data)

### Frontend Implementation for User Story 4

- [ ] T176 [US4] Create auth API client in frontend/src/features/auth/api/authApi.ts
- [ ] T177 [US4] Enhance useAuth hook with login, logout, and token refresh
- [ ] T178 [P] [US4] Create LoginForm component in frontend/src/features/auth/components/LoginForm.tsx
- [ ] T179 [US4] Create LoginPage in frontend/src/pages/LoginPage.tsx
- [ ] T180 [US4] Add protected route wrapper for admin pages
- [ ] T181 [US4] Add automatic token refresh logic

### Integration & Validation for User Story 4

- [ ] T182 [US4] Run all US4 tests and ensure they pass
- [ ] T183 [US4] Manual test: Login as Brand A admin, verify cannot access Brand B data via API
- [ ] T184 [US4] Manual test: Verify super_admin can access all brands

**Checkpoint**: User Story 4 complete - multi-brand permission system functional

---

## Phase 7: User Story 5 - AI 擴充預留接口 (Priority: P5)

**Goal**: 系統預留標準化的 AI 模組接口，目前階段僅需定義接口規格和回傳模擬資料的 stub 實作

**Independent Test**: 呼叫 AI 推薦 API 接口，系統回傳符合預定義格式的模擬推薦結果

### Backend Tests for User Story 5 (Write First - TDD) ⚠️

- [ ] T185 [P] [US5] Contract test for GET /brands/{slug}/recommendations endpoint in backend/tests/integration/api/test_ai_api.py
- [ ] T186 [P] [US5] Unit test for AIService stub in backend/tests/unit/infrastructure/ai/test_ai_service_stub.py

### Backend Application Layer for User Story 5

- [ ] T187 [P] [US5] Create AIService interface in backend/src/application/interfaces/ai_service.py (recommend_items, predict_demand methods)

### Backend Infrastructure Layer for User Story 5

- [ ] T188 [US5] Create AIService stub implementation in backend/src/infrastructure/ai/ai_service_stub.py

### Backend API Layer for User Story 5

- [ ] T189 [P] [US5] Create AI Pydantic schemas in backend/src/api/v1/schemas/ai_schemas.py
- [ ] T190 [US5] Implement AI routes in backend/src/api/v1/routes/ai.py (GET /brands/{slug}/recommendations)

### Frontend Implementation for User Story 5

- [ ] T191 [US5] Create AI API client in frontend/src/features/ai/api/aiApi.ts
- [ ] T192 [US5] Create useRecommendations hook in frontend/src/features/ai/hooks/useRecommendations.ts
- [ ] T193 [P] [US5] Create RecommendedItems component in frontend/src/features/ai/components/RecommendedItems.tsx
- [ ] T194 [US5] Integrate RecommendedItems component into MenuPage

### Integration & Validation for User Story 5

- [ ] T195 [US5] Run all US5 tests and ensure they pass
- [ ] T196 [US5] Manual test: Verify AI endpoint returns mock recommendations in correct format
- [ ] T197 [US5] Document AI interface for future ML model integration

**Checkpoint**: User Story 5 complete - AI interface ready for future integration

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Shared Components & UI Polish

- [ ] T198 [P] Create Button component in frontend/src/shared/components/Button.tsx (using Headless UI)
- [ ] T199 [P] Create Modal component in frontend/src/shared/components/Modal.tsx (using Headless UI Dialog)
- [ ] T200 [P] Create Input component in frontend/src/shared/components/Input.tsx
- [ ] T201 [P] Create Dropdown component in frontend/src/shared/components/Dropdown.tsx (using Headless UI Listbox)
- [ ] T202 [P] Create CustomerLayout in frontend/src/layouts/CustomerLayout.tsx
- [ ] T203 [P] Create AdminLayout in frontend/src/layouts/AdminLayout.tsx

### Error Handling & Validation

- [ ] T204 Add comprehensive error handling to all API endpoints with specific error codes
- [ ] T205 Add input validation for all Pydantic schemas with clear error messages
- [ ] T206 Add frontend form validation with user-friendly error messages
- [ ] T207 Create error boundary component in frontend/src/shared/components/ErrorBoundary.tsx

### Performance Optimization

- [ ] T208 Add database indexes per data-model.md specifications
- [ ] T209 Optimize menu loading query with JOINs to avoid N+1 problem
- [ ] T210 Add caching to frequently accessed brand theme data
- [ ] T211 Implement lazy loading for menu images

### Security Hardening

- [ ] T212 Add rate limiting to public endpoints (100 req/min/IP)
- [ ] T213 Add CSRF protection to form submissions
- [ ] T214 Add Content Security Policy headers
- [ ] T215 Audit all queries for SQL injection vulnerabilities
- [ ] T216 Add logging for all authentication failures and permission denials

### Documentation & Testing

- [ ] T217 [P] Write unit tests for all shared frontend components in frontend/tests/unit/shared/components/
- [ ] T218 [P] Write integration tests for brand isolation in backend/tests/integration/test_brand_isolation.py
- [ ] T219 [P] Write E2E test for admin workflow in frontend/tests/e2e/admin-flow.spec.ts
- [ ] T220 Update README.md with setup instructions
- [ ] T221 Verify quickstart.md instructions are accurate
- [ ] T222 Generate API documentation from OpenAPI spec

### Code Quality & Refactoring

- [ ] T223 Run ruff check on backend and fix all linting errors
- [ ] T224 Run ESLint on frontend and fix all linting errors
- [ ] T225 Refactor duplicate code into shared utilities
- [ ] T226 Add type hints to all Python functions
- [ ] T227 Add JSDoc comments to all TypeScript functions

### Final Validation

- [ ] T228 Run all backend tests: pytest backend/tests/ --cov=src --cov-report=html
- [ ] T229 Run all frontend tests: cd frontend && pnpm test && pnpm test:e2e
- [ ] T230 Verify test coverage >= 80% for backend
- [ ] T231 Manual test: Complete end-to-end customer ordering flow
- [ ] T232 Manual test: Complete end-to-end admin workflow
- [ ] T233 Manual test: Verify three brands can operate independently
- [ ] T234 Performance test: Verify API response times < 200ms (p95)
- [ ] T235 Security test: Attempt to access Brand A data as Brand B admin (should fail)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses Brand and Menu entities from US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Analyzes Order data from US2 but should work with test data
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances auth system from Foundational phase
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Completely independent stub implementation

### Within Each User Story - TDD Workflow

1. **Tests FIRST** (marked with ⚠️): Write all tests for the user story, ensure they FAIL
2. **Domain entities**: Create core business entities and value objects
3. **Domain services**: Implement business logic
4. **Application use cases**: Orchestrate domain services
5. **Infrastructure repositories**: Implement data persistence
6. **API routes**: Expose functionality via REST endpoints
7. **Frontend components**: Build user interface
8. **Integration validation**: Run all tests, ensure they PASS
9. **Manual testing**: Verify story works end-to-end

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - 白牌化核心!)
3. Add User Story 2 → Test independently → Deploy/Demo (訂餐功能)
4. Add User Story 3 → Test independently → Deploy/Demo (Analytics)
5. Add User Story 4 → Test independently → Deploy/Demo (多品牌管理)
6. Add User Story 5 → Test independently → Deploy/Demo (AI 預留)
7. Polish → Final release
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (白牌化核心)
   - Developer B: User Story 2 (訂餐流程)
   - Developer C: Authentication system from US4
3. Stories complete and integrate independently
4. Then move to User Stories 3, 4, 5 in priority order

---

## Test Summary by User Story

| User Story | Backend Tests | Frontend Tests | Total Tests |
|------------|---------------|----------------|-------------|
| US1 - 品牌快速上線 | 11 tests (T042-T052) | 4 tests (T077-T080) | 15 tests |
| US2 - 顧客訂餐流程 | 7 tests (T097-T103) | 4 tests (T118-T121) | 11 tests |
| US3 - 營運數據分析 | 4 tests (T137-T140) | 2 tests (T149-T150) | 6 tests |
| US4 - 品牌權限管理 | 3 tests (T163-T165) | 0 tests | 3 tests |
| US5 - AI 擴充接口 | 2 tests (T185-T186) | 0 tests | 2 tests |
| **Total** | **27 tests** | **10 tests** | **37 tests** |

---

## Task Count Summary

| Phase | Task Count | Estimated Days |
|-------|------------|----------------|
| Phase 1: Setup | 12 tasks | 1-2 days |
| Phase 2: Foundational | 29 tasks | 5-7 days |
| Phase 3: User Story 1 | 55 tasks | 10-12 days |
| Phase 4: User Story 2 | 40 tasks | 7-9 days |
| Phase 5: User Story 3 | 26 tasks | 5-6 days |
| Phase 6: User Story 4 | 22 tasks | 4-5 days |
| Phase 7: User Story 5 | 13 tasks | 2-3 days |
| Phase 8: Polish | 38 tasks | 5-7 days |
| **Total** | **235 tasks** | **39-51 days** |

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD Workflow is NON-NEGOTIABLE**: Write tests first, ensure they fail, then implement
- Verify tests fail before implementing (red → green → refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Success Criteria Mapping

This implementation plan addresses all success criteria from spec.md:

- **SC-001**: US1 T093-T096 - Brand onboarding in 10 minutes
- **SC-002**: US2 T135 - Order flow in 3 minutes
- **SC-003**: US1 T096 + US4 T183 - Three brands operating independently
- **SC-004**: US1 T095 - Theme updates reflect in 5 seconds
- **SC-005**: US3 T161 - Analytics load in 2 seconds
- **SC-006**: T234 - Performance test for 100 orders/minute
- **SC-007**: US4 T183 + T235 - Brand data isolation 100% enforced
- **SC-008**: US2 T135 - Order lookup in 1 second
- **SC-009**: US5 T196 - AI stub returns in 500ms
- **SC-010**: US1 T095 - Third-party menu JSON import without code changes

---

**END OF TASKS.MD**
