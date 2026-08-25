# SPECIFICATION: Kitchen Online Ordering Ecosystem (Telegram Mini App + Windows Kitchen Client)

> **Target Platform / Stack:** FastAPI (Python 3.11+) | Vue 3 (Pinia + Tailwind) | Electron/PyQt (Windows Client) | PostgreSQL 15+ | Railway.app  
> **Region / Currency:** South Korea (KST / Asia/Seoul) | KRW (₩)  
> **Primary Language:** Russian (UI & Bot), Korean (Receipt/Address compatibility)

---

## 1. Project Overview & System Architecture

The ecosystem provides an end-to-end food ordering solution for a kitchen in South Korea. It streamlines orders via Telegram WebApp (Mini App), manual bank wire transfer verification via screenshot attachments, kitchen order dispatch via a loud Windows desktop client, and full owner control via an in-app admin panel with broadcast marketing.

```
+-----------------------------------------------------------------------------------+
|                                  USER / CLIENT                                    |
+-----------------------------------------------------------------------------------+
       |                                                    ^
       | 1. /start & Open WebApp                            | 8. Order Status Push
       v                                                    |
+----------------------+       2. InitData & REST     +-----------------------------+
| Telegram Mini App    | ---------------------------> | Backend API (FastAPI)       |
| (Vue 3 + Pinia + UI) | <--------------------------- | - Auth & HMAC InitData      |
+----------------------+       State & Data           | - Order & Menu CRUD         |
                                                      | - Media Handler (Receipts)  |
+----------------------+       Config & Sync          | - Broadcast Queue Engine    |
| Mobile Admin Panel   | ---------------------------> | - PostgreSQL 15+            |
| (Embedded in Vue 3)  |                              +-----------------------------+
+----------------------+                                    |            |
                                      3. New Order Dispatch |            | 4. WS Stream
                                                            v            v
                                              +---------------+  +------------------+
                                              | Telegram Bot  |  | Windows Kitchen  |
                                              | (Owner Chat)  |  | Client (Desktop) |
                                              +---------------+  +------------------+
                                              | Inline Action |  | Loop Siren Alarm |
                                              | (Accept/Reject|  | Large Order Card |
                                              +---------------+  +------------------+
```

---

## 2. Directory Structure

```text
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py          # Telegram WebApp InitData HMAC validator
│   │   │   │   ├── menu.py          # Categories & menu items
│   │   │   │   ├── orders.py        # Order creation, upload receipt, status
│   │   │   │   ├── admin.py         # Admin controls, clients stats, broadcast
│   │   │   │   └── ws.py            # WebSocket kitchen endpoint
│   │   ├── core/
│   │   │   ├── config.py        # Settings & Env vars
│   │   │   ├── database.py      # SQLAlchemy async session
│   │   │   └── security.py      # HMAC signature validation
│   │   ├── models/              # SQLAlchemy Models
│   │   ├── schemas/             # Pydantic Schemas
│   │   ├── services/
│   │   │   ├── bot.py           # Aiogram bot instance & notifications
│   │   │   ├── broadcast.py     # Batch broadcast queue runner
│   │   │   └── storage.py       # Receipt image processing
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                        # Telegram Mini App (Client + Admin)
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── CartDrawer.vue
│   │   │   ├── MenuItemCard.vue
│   │   │   ├── CheckoutModal.vue
│   │   │   └── admin/
│   │   │       ├── StopListManager.vue
│   │   │       ├── BroadcastSender.vue
│   │   │       └── ClientAnalytics.vue
│   │   ├── views/
│   │   │   ├── MenuCatalogView.vue
│   │   │   ├── OrderSuccessView.vue
│   │   │   └── AdminDashboardView.vue
│   │   ├── stores/
│   │   │   ├── user.js          # Telegram user info, auto-fill profile
│   │   │   ├── cart.js          # Cart items, delivery fee calculation
│   │   │   └── menu.js          # Menu data, categories
│   │   ├── App.vue
│   │   └── main.js
│   ├── vite.config.js
│   ├── package.json
│   └── tailwind.config.js
├── kitchen-app/                     # Windows Desktop Alarm Receiver
│   ├── main.js                      # Electron / Tauri main process
│   ├── index.html                   # High-contrast fullscreen order UI
│   ├── renderer.js                  # WebSocket listener & Audio siren looper
│   ├── sound/
│   │   └── alarm.mp3                # Continuous siren audio
│   └── package.json
├── docker-compose.yml
└── SPEC.md
```

---

## 3. Database Schema (PostgreSQL DDL)

```sql
-- Client User Profiles & Activity Analytics
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(64),
    first_name VARCHAR(128),
    last_name VARCHAR(128),
    phone VARCHAR(32),
    saved_address TEXT,
    last_delivery_type VARCHAR(16) DEFAULT 'delivery',
    is_admin BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Food Categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    sort_order INT DEFAULT 0
);

-- Menu Items & Stop-List
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    price INT NOT NULL, -- in KRW (₩)
    image_url TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customer Orders
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    order_type VARCHAR(16) NOT NULL, -- 'delivery' | 'pickup'
    phone VARCHAR(32) NOT NULL,
    address TEXT,
    comment TEXT,
    items_total INT NOT NULL,
    delivery_fee INT DEFAULT 0,
    total_amount INT NOT NULL,
    payment_screenshot_url TEXT NOT NULL,
    status VARCHAR(32) DEFAULT 'pending', -- 'pending' | 'accepted' | 'cooking' | 'shipped' | 'cancelled'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Order Items Detail
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INT REFERENCES menu_items(id) ON DELETE SET NULL,
    item_name VARCHAR(128) NOT NULL,
    price INT NOT NULL,
    quantity INT NOT NULL
);

-- Global Kitchen & Store Settings
CREATE TABLE settings (
    key VARCHAR(64) PRIMARY KEY,
    value JSONB NOT NULL
);
-- Keys expected: 'store_schedule', 'is_open_override', 'bank_details', 'delivery_fee'
```

---

## 4. API Specifications & Data Contracts

### 4.1. Telegram InitData Authentication
Every request from Mini App must pass `Authorization: tma <initDataRaw>` header. Backend verifies HMAC-SHA256 signature using `BOT_TOKEN`.
```python
# Auth Payload parsed:
{
    "telegram_id": 123456789,
    "first_name": "Alex",
    "username": "alex_kr",
    "is_admin": True  # evaluated against ADMIN_TELEGRAM_IDS
}
```

### 4.2. Core Endpoints

#### `POST /api/v1/auth/telegram`
* **Purpose:** Validates `initData`, updates `last_active`, returns user profile and admin privileges.
* **Response:**
```json
{
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "phone": "010-1234-5678",
    "saved_address": "평택시 중앙로 12, 101호",
    "last_delivery_type": "delivery",
    "is_admin": true
  },
  "settings": {
    "is_open": true,
    "delivery_fee": 3000,
    "bank_details": {
      "bank": "KB Kookmin Bank",
      "account": "123-4567-890123",
      "holder": "KIM OWNER"
    }
  }
}
```

#### `POST /api/v1/orders` (Multipart Form Data)
* **Payload:**
  * `order_type`: `delivery` | `pickup`
  * `phone`: `010-XXXX-XXXX`
  * `address`: string (if delivery)
  * `comment`: string
  * `items`: JSON string `[{"menu_item_id": 1, "quantity": 2}, ...]`
  * `receipt_image`: Binary file (image/jpeg, image/png)
* **Actions triggered on creation:**
  1. Inserts order into DB.
  2. Broadcasts JSON payload to `/ws/kitchen` for the Windows client.
  3. Sends photo message with inline keyboard to Owner Telegram Chat.
  4. Returns `order_id` to client.

#### `WS /ws/kitchen?token=<KITCHEN_WS_SECRET>`
* Realtime stream pushing new orders directly to Windows Kitchen Client.
* **Frame format:**
```json
{
  "event": "NEW_ORDER",
  "order": {
    "id": 108,
    "order_type": "delivery",
    "created_at": "2026-08-25T13:00:00+09:00",
    "phone": "010-9876-5432",
    "address": "평택시 중앙ло 12, 101호",
    "comment": "Код домофона #1234, острее пожалуйста",
    "items": [
      {"name": "Кимчи тиге", "qty": 1, "price": 9000},
      {"name": "Самгёпсаль сет", "qty": 2, "price": 28000}
    ],
    "delivery_fee": 3000,
    "total_amount": 40000,
    "screenshot_url": "https://api.domain.com/uploads/receipt_108.jpg"
  }
}
```

#### `POST /api/v1/admin/broadcast`
* **Payload:**
```json
{
  "message_text": "Скидка 15% на все сеты только сегодня! 🥩",
  "image_url": "https://.../promo.jpg"
}
```
* **Engine:** Background task iterating over all `users.telegram_id` with rate-limiting ($25\text{ msg/sec}$) and handling `BotBlocked` exceptions gracefully.

---

## 5. UI/UX & Client Logic Requirements

### 5.1. Telegram Mini App (Vue 3)
1. **Operating Hours Guard:** Check current time vs. kitchen operating schedule (KST). If closed and not overridden, display a full-banner overlay and lock checkout buttons.
2. **Smart Checkout Auto-Fill:**
   * Automatically populate `phone`, `address`, and `order_type` from previous user profile.
   * Format phone number to Korean telecom format (`010-XXXX-XXXX`).
3. **Receipt Attachment:** User must upload proof of payment before submission. The client previews the image before sending.
4. **Copy-to-Clipboard:** Quick copy button for bank account number.

### 5.2. In-App Mobile Admin Panel
* Rendered conditionally if `user.is_admin === true`.
* **Features:**
  * Toggle item stock availability in 1 click (Stop-List).
  * Edit prices and add new dishes with photo upload.
  * Kitchen status toggle (Emergency Open/Close).
  * User Activity list (Sorted by `last_active`, total orders count, total KRW spent).
  * Broadcast Composer with "Send test to me" button.

### 5.3. Windows Kitchen Client
* **Target:** Standalone Windows App (`.exe`).
* **Display:** Full-screen kiosk layout with high contrast (dark theme, large typography).
* **Audio Engine:** Loops `alarm.mp3` continuously upon `NEW_ORDER` event until the user clicks `[ Заказ принят / Отключить сирену ]`.
* **Resilience:** Auto-reconnects to WebSocket on network hiccups using exponential backoff (1s, 2s, 5s, 10s).

---

## 6. Deployment & Environment Variables (Railway.app)

### 6.1. Environment Configuration (`.env`)
```ini
# Core
PROJECT_NAME="Kitchen Barakat"
TZ="Asia/Seoul"

# Telegram Bot
BOT_TOKEN="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ADMIN_TELEGRAM_IDS="123456789,987654321"
OWNER_CHAT_ID="-1001234567890"

# Security
KITCHEN_WS_SECRET="super_secret_kitchen_token_key"
CORS_ORIGINS="https://your-frontend.up.railway.app,https://web.telegram.org"

# Database (Railway Postgres default variable)
DATABASE_URL="postgresql+asyncpg://postgres:password@roundhouse.railway.internal:5432/railway"

# Business Defaults
DEFAULT_DELIVERY_FEE=3000
BANK_NAME="KB Kookmin Bank"
BANK_ACCOUNT="123-4567-890123"
BANK_HOLDER="KIM OWNER"
```

### 6.2. Railway Services Topology
1. **Service 1: PostgreSQL** (Standard Railway Database addon).
2. **Service 2: Backend & Bot** (Docker build from `/backend` running Uvicorn + Aiogram polling/webhook).
3. **Service 3: Frontend WebApp** (Vite build served as static site with custom HTTPS domain).

---

## 7. Implementation Roadmap & Acceptance Criteria

* [ ] **Phase 1: DB & API Core** — Setup DB schema, Telegram initData HMAC verification, CRUD for Menu & Orders.
* [ ] **Phase 2: Vue 3 Mini App** — Menu catalog, reactive cart, Korean address/phone auto-fill, receipt upload, Admin tab.
* [ ] **Phase 3: Bot Notifications & Broadcast** — Owner chat notifications with inline status buttons, rate-limited broadcast engine.
* [ ] **Phase 4: Windows Desktop Client** — Electron/Tauri app, WebSocket client, continuous siren loop, receipt viewer.
* [ ] **Phase 5: Railway Deploy & E2E Testing** — Production environment config, end-to-end order simulation.
