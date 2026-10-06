# FabricFlow Analytics – A Data-Driven Approach for Garment Inventory Analysis

FabricFlow Analytics is a comprehensive, production-ready garment inventory management, demand forecasting, and analytics web application. It connects an intuitive HTML5/CSS/Vanilla JavaScript frontend to a Python Flask backend, backed by **Google Cloud Firestore** (via the Firebase Admin SDK), and powers data-driven inventory intelligence using **Pandas** and **NumPy**.

---

## 1. Technology Stack

- **Backend**: Python 3.10+, Flask 3.0+, Flask-CORS, Gunicorn
- **Database**: Google Cloud Firestore (NoSQL Document Store via Firebase Admin SDK)
- **Analytics & Forecasting**: Pandas & NumPy (Sales velocity, stock classification, demand projection)
- **Frontend**: Semantic HTML5, Vanilla CSS3 (Custom design system), Vanilla JavaScript (ES6+), Chart.js
- **Authentication**: Firebase Authentication & Firebase Admin SDK Token Verification
- **Reporting**: Dynamic CSV stream generators for Inventory, Sales, Products, Low-Stock, and Forecasts

---

## 2. System Architecture

```
Frontend (HTML5 / Vanilla CSS / Vanilla JS / Chart.js)
    │  (Centralized API client via frontend/js/common.js)
    ▼
Flask Application Layer (app.py, Blueprints, CORS, Error Handlers, Auth)
    │
    ├──▶ Services Layer (Product, Category, Supplier, Inventory, Sales, Dashboard, Report)
    │        │
    │        ├──▶ Analytics Engine (Pandas & NumPy: sales velocity & demand forecasting)
    │        │
    │        ▼
    └────▶ Firebase Admin SDK (firebase/firebase_config.py)
                 │
                 ▼
          Google Cloud Firestore (Live NoSQL Cloud Collections)
          ├── users
          ├── products
          ├── categories
          ├── inventory
          ├── sales
          └── suppliers
```

---

## 3. Firebase & Cloud Firestore Setup

1. **Create a Firebase Project**:
   - Navigate to the [Firebase Console](https://console.firebase.google.com/).
   - Click **Add Project** and give it a name (e.g. `fabricflow-553fb`).
2. **Enable Cloud Firestore**:
   - In the left sidebar, click **Build** ➔ **Firestore Database**.
   - Click **Create Database**.
   - Select your preferred cloud region and choose **Production mode** (or Test mode during initial setup).
3. **Firestore Collections**:
   The system utilizes the following Firestore collections:
   - `users`: User profiles with roles (`admin`, `manager`, `staff`).
   - `products`: Garment master catalog (sizes, prices, suppliers, categories).
   - `categories`: Clothing categories (e.g., Casual Wear, Denim, Ethnic Wear, Formal Wear, etc.).
   - `inventory`: Real-time stock levels, reorder thresholds, and dynamic status (`Normal`, `Low`, `Critical`).
   - `sales`: Transaction receipts and line items.
   - `suppliers`: Textile mills and garment vendors.

---

## 4. Service Account Setup (Firebase Admin SDK)

1. In the Firebase Console, navigate to **Project Settings** (gear icon) ➔ **Service accounts**.
2. Select **Python** and click **Generate new private key**.
3. Download the JSON credential file and place it in the project root or backend folder:
   ```
   backend/serviceaccountkey.json
   ```
4. **DO NOT commit this file to GitHub or any public repository**. Ensure it is listed in `.gitignore`.

---

## 5. Local Installation

### Prerequisites
- Python 3.10 or higher
- Git

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd fabricflow

# 2. Create and activate a Python virtual environment
python -m venv venv

# Windows (Command Prompt / PowerShell):
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt
```

---

## 6. Environment Variables Configuration

Copy the example file to create your active configuration:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
FLASK_APP=app.py
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
SECRET_KEY=fabricflow-secure-jwt-key-2024

# Firebase Admin SDK Credentials
FIREBASE_CREDENTIALS_PATH=backend/serviceaccountkey.json
FIREBASE_PROJECT_ID=fabricflow-553fb

# Inventory Thresholds
DEFAULT_CRITICAL_STOCK_THRESHOLD=5
DEFAULT_LOW_STOCK_THRESHOLD=20
```

---

## 7. How to Seed Firestore with Demo Garment Data

To populate your Cloud Firestore project with initial categories, suppliers, garment products, inventory tracking records, and historical sales transactions:

```bash
python firestore/seed_data.py
```

*Note: The seed script checks for existing documents and safely merges records without destructive drops by default.*

---

## 8. How to Run the Application

### Development Server:
```bash
python app.py
```
Or:
```bash
flask run --host=0.0.0.0 --port=5000
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
or open `frontend/index.html` or `frontend/pages/dashboard.html`.

### Production Server:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 9. Running Tests

Run the full automated test suite (including Firestore CRUD, analytics, and end-to-end flows):

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Or run the specific end-to-end integration flow:
```bash
python -m unittest tests/test_end_to_end.py
```

---

## 10. REST API Specification

### Health & Connectivity
- `GET /api/health` — Verifies Flask backend and performs a live Firestore connection probe.

### Products
- `GET /api/products` — Retrieve all products (supports `?search=`, `?category=`, `?size=`, `?status=`).
- `POST /api/products` — Create a product and automatically initialize its Firestore inventory record.
- `GET /api/products/<product_id>` — Fetch product by ID.
- `PUT /api/products/<product_id>` — Update product details and timestamps.
- `DELETE /api/products/<product_id>` — Safely delete product from catalog.

### Categories
- `GET /api/categories` — List all garment categories.
- `POST /api/categories` — Add category (validates duplicate names).
- `PUT /api/categories/<category_id>` — Update category name/description.
- `DELETE /api/categories/<category_id>` — Remove category.

### Suppliers
- `GET /api/suppliers` — List all textile and garment suppliers.
- `POST /api/suppliers` — Register a supplier.
- `GET /api/suppliers/<supplier_id>` — Get supplier profile.
- `PUT /api/suppliers/<supplier_id>` — Update supplier contact/address.
- `DELETE /api/suppliers/<supplier_id>` — Delete supplier.

### Inventory Management
- `GET /api/inventory` — List all stock records with calculated stock status (`Normal`, `Low`, `Critical`).
- `GET /api/inventory/<product_id>` — Retrieve stock details for a specific item.
- `PUT /api/inventory/<product_id>` — Update reorder level or quantity.
- `POST /api/inventory/<product_id>/adjust` — Adjust stock with types: `add`, `deduct`, `set`. Enforces non-negative stock constraint and recalculates status.

### Sales Management
- `GET /api/sales` — List sales transactions (supports `?search=`, `?category=`, `?limit=`).
- `POST /api/sales` — Atomic Firestore batch transaction: validates stock, creates sale record, decrements inventory, and updates stock status.
- `GET /api/sales/<sale_id>` — Get single sale receipt.
- `DELETE /api/sales/<sale_id>` — Cancel/delete sale entry.

### Dashboard
- `GET /api/dashboard` — Aggregates live Firestore metrics: `total_products`, `total_stock`, `total_sales`, `low_stock_items`, `critical_stock_items`, `sales_trend`, `stock_status`, `top_categories`, `recent_sales`.

### Analytics (Pandas & NumPy)
- `GET /api/analytics` — Consolidated analytics payload.
- `GET /api/analytics/sales` — Daily distribution, monthly trends, and category revenue share.
- `GET /api/analytics/inventory` — Stock distribution across categories and stock health breakdown.
- `GET /api/analytics/products` / `/performance` — Sales velocity calculation (`sales_velocity = quantity_sold / number_of_days`) and classification into Fast-Moving, Normal-Moving, and Slow-Moving.

### Demand Forecasting
- `GET /api/forecast?period=7|30|90` — Mathematical demand forecast based on average daily sales and dynamic safety stock recommendations (`Increase Stock`, `Maintain Stock`, `Reduce Stock`).

### Reports & CSV Export
- `GET /api/reports/inventory?format=csv` — Inventory status report.
- `GET /api/reports/sales?format=csv` — Sales transaction audit report.
- `GET /api/reports/products?format=csv` — Product catalog performance report.
- `GET /api/reports/low-stock?format=csv` — Low and critical stock exception report.
- `GET /api/reports/forecast?format=csv` — Demand projection and replenishment report.

---

## 11. Frontend Configuration

The frontend interacts with the backend through a centralized API configuration in **`frontend/js/common.js`**:

```javascript
// Change this single constant to re-point all pages for production deployment
const API_BASE_URL = "http://127.0.0.1:5000/api";
```

All frontend modules use the centralized `apiRequest(endpoint, options)` helper which handles:
- Dynamic HTTP methods (`GET`, `POST`, `PUT`, `DELETE`)
- JSON payload serializing & parsing
- Authorization Bearer tokens
- Standardized error toast notifications

---

## 12. Security Instructions

1. **Do NOT Commit Credentials**:
   - `backend/serviceaccountkey.json` contains Google Cloud private keys and is explicitly ignored in `.gitignore`.
   - Never push `.env` or any `*.json` file containing `private_key` to Git or public hosting.
2. **Backend Authentication**:
   - Protected endpoints utilize the `backend/utils/auth.py` decorator `require_auth` verifying Firebase ID tokens via the Firebase Admin SDK.
   - User roles (`admin`, `manager`, `staff`) are verified server-side against Firestore `users` records and never trusted directly from client cookies or query params.
3. **CORS Restrictions**:
   - In production, specify authorized origins in `.env` (e.g. `CORS_ORIGINS=https://your-domain.com`) instead of wildcard origins.
4. **Zero Client Credentials**:
   - The frontend communicates only with the Flask API via JSON; the Firebase private key is never exposed or transmitted to the browser.
