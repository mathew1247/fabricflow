# FabricFlow Analytics — Complete REST API Documentation

Base URL: `http://localhost:5000/api`

---

## 🔐 1. Authentication (`/api/auth`)

### `POST /api/auth/login`
Authenticates an administrator or staff user.
- **Request Body:**
```json
{
  "email": "admin@fabricflow.com",
  "password": "fabricflow2024"
}
```
- **Response (200 OK):**
```json
{
  "status": "success",
  "message": "Authentication successful.",
  "data": {
    "uid": "ff-admin-001",
    "name": "Alex Morgan",
    "email": "admin@fabricflow.com",
    "role": "Inventory Admin",
    "token": "fabricflow2024"
  }
}
```

### `GET /api/auth/me`
Fetches authenticated user profile. Requires Bearer Token.

### `POST /api/auth/logout`
Terminates current session.

---

## 👕 2. Products (`/api/products`)

### `GET /api/products`
Query parameters:
- `search` (string): Search by name, SKU, or supplier
- `category` (string): Filter by Casual, Denim, Formal, Outerwear
- `size` (string): Filter by size (S, M, L, XL, 30, 32, 34)
- `status` (string): Filter by Normal, Low, Critical

### `GET /api/products/<product_id>`
Retrieves a single garment product by ID.

### `POST /api/products`
Creates a new garment product in Cloud Firestore.
```json
{
  "id": "P013",
  "name": "Oversized Corduroy Overshirt",
  "category": "Casual",
  "size": "L",
  "price": 2199,
  "cost_price": 1100,
  "supplier": "ABC Textiles",
  "stock": 60,
  "min_stock": 20
}
```

### `PUT /api/products/<product_id>`
Updates an existing product.

### `DELETE /api/products/<product_id>`
Deletes a product from Firestore.

---

## 🏷 3. Categories (`/api/categories`)

### `GET /api/categories`
Returns all garment classifications with item counts.

---

## 📦 4. Inventory (`/api/inventory`)

### `GET /api/inventory`
Returns inventory list with calculated stock status (`Normal`, `Low`, `Critical`).

### `GET /api/inventory/summary`
Returns top-level stock metrics:
```json
{
  "status": "success",
  "data": {
    "total_stock_units": 18540,
    "total_valuation": 15420000.0,
    "normal_pct": 75,
    "low_pct": 18,
    "critical_pct": 7,
    "stock_turnover_ratio": 4.8
  }
}
```

### `POST /api/inventory/<product_id>/adjust`
Performs stock inflow, deduction, or exact count audit:
```json
{
  "type": "add",
  "quantity": 25,
  "reason": "Batch arrival from textile mill"
}
```

---

## 🛒 5. Sales Orders (`/api/sales`)

### `GET /api/sales`
Returns sales transactions. Query params: `search`, `category`, `status`, `limit`.

### `GET /api/sales/<sale_id>`
Returns invoice details.

### `POST /api/sales`
Records sale and **automatically updates stock in Firestore** when status is `Completed`:
```json
{
  "product": "Classic Cotton T-Shirt",
  "category": "Casual",
  "quantity": 5,
  "unit_price": 899,
  "status": "Completed",
  "date": "2024-09-10"
}
```

---

## 🚚 6. Suppliers (`/api/suppliers`)

### `GET /api/suppliers`
List suppliers directory with contact and mill details.

### `POST /api/suppliers`
Creates a new supplier.

### `PUT /api/suppliers/<supplier_id>`
Updates supplier profile.

### `DELETE /api/suppliers/<supplier_id>`
Deletes a supplier.

---

## 📊 7. Dashboard Overview (`/api/dashboard`)

### `GET /api/dashboard?period=monthly|weekly|quarterly`
Consolidated payload for KPI cards, sales trend area coordinates, stock status donut, top category progress bars, and recent sales.

---

## 📈 8. Analytics (`/api/analytics`)

- `GET /api/analytics` — Composite analytics data payload.
- `GET /api/analytics/sales` — Sales trends, category distributions, monthly vs target.
- `GET /api/analytics/inventory` — Stock distribution, inventory inflow/outflow velocity.
- `GET /api/analytics/performance` — Fast-moving and slow-moving product tables.

---

## 🎯 9. Demand Forecasting (`/api/forecast`)

### `GET /api/forecast?period=7|30|90&category=all|Casual|...`
Computes statistical demand forecasts, trajectory curves, and safety-buffered procurement advice.

---

## 📑 10. Reports (`/api/reports`)

### `GET /api/reports/preview?type=inventory|sales|lowstock|performance|forecast`
Returns tabular preview data.

### `GET /api/reports/export/csv?type=inventory|sales|lowstock|performance|forecast`
Downloads generated CSV file stream.
