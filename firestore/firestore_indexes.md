# Firebase Cloud Firestore Indexing Configuration

To maximize query speed and support multi-field filtering and sorting on large garment inventories, deploy the following composite indexes in the Firebase Console under **Firestore Database** ➔ **Indexes** or using the Firebase CLI (`firebase.json`).

---

## 1. Products Collection Indexes

| Collection ID | Fields Indexed | Query Scope | Purpose |
|---|---|---|---|
| `products` | `category` (Ascending), `price` (Ascending) | Collection | Filter products by category and sort by price |
| `products` | `category` (Ascending), `stock` (Ascending) | Collection | Filter products by category and identify low stock items |
| `products` | `status` (Ascending), `stock` (Ascending) | Collection | Filter products by Critical/Low status and sort by lowest stock |
| `products` | `supplier` (Ascending), `name` (Ascending) | Collection | Filter products by supplier |

---

## 2. Sales Collection Indexes

| Collection ID | Fields Indexed | Query Scope | Purpose |
|---|---|---|---|
| `sales` | `status` (Ascending), `date` (Descending) | Collection | Filter completed/pending orders sorted by newest |
| `sales` | `category` (Ascending), `date` (Descending) | Collection | Category sales time-series extraction |
| `sales` | `date` (Descending), `total` (Descending) | Collection | High-value order audits over date ranges |

---

## 3. Deployment via Firebase CLI (`firestore.indexes.json`)

```json
{
  "indexes": [
    {
      "collectionGroup": "products",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "category", "order": "ASCENDING" },
        { "fieldPath": "price", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "products",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "stock", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "sales",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "date", "order": "DESCENDING" }
      ]
    }
  ],
  "fieldOverrides": []
}
```
