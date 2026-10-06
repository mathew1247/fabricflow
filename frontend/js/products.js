/**
 * FABRICFLOW ANALYTICS - PRODUCTS MANAGEMENT SCRIPT
 * Production-ready CRUD connected to Flask REST API /api/products & Cloud Firestore
 */

let productsList = [];
let deleteTargetId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  setupEventListeners();
});

// API Integration Functions
async function loadProducts() {
  const tableBody = document.getElementById("productsTableBody");
  if (tableBody && productsList.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; padding: 2.5rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-spinner fa-spin" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
          <span>Loading products from Cloud Firestore...</span>
        </td>
      </tr>
    `;
  }

  try {
    const res = await apiRequest("/products");
    productsList = res.data || [];
    renderProductsTable();
    populateSupplierSelect();
  } catch (err) {
    console.error("Failed to load products from API:", err.message);
    showToast("Failed to load products: " + err.message, "error");
    if (tableBody) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align:center; padding: 2.5rem 1rem; color: var(--danger);">
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
            <span>Error connecting to server. Please ensure backend is running.</span>
          </td>
        </tr>
      `;
    }
  }
}

async function addProduct(productData) {
  try {
    await apiRequest("/products", "POST", productData);
    showToast(`Product "${productData.product_name || productData.name}" added to Firestore!`, "success");
    await loadProducts();
  } catch (err) {
    console.error("API add product failed:", err.message);
    showToast(`Failed to add product: ${err.message}`, "error");
  }
}

async function updateProduct(id, updatedData) {
  try {
    await apiRequest(`/products/${id}`, "PUT", updatedData);
    showToast(`Product "${updatedData.product_name || updatedData.name}" updated successfully!`, "success");
    await loadProducts();
  } catch (err) {
    console.error("API update product failed:", err.message);
    showToast(`Failed to update product: ${err.message}`, "error");
  }
}

async function deleteProduct(id) {
  try {
    await apiRequest(`/products/${id}`, "DELETE");
    showToast("Product deleted successfully from Firestore.", "success");
    await loadProducts();
  } catch (err) {
    console.error("API delete product failed:", err.message);
    showToast(`Failed to delete product: ${err.message}`, "error");
  }
}

function calculateStockStatus(stock, minStock = 20) {
  if (stock <= 5) return "Critical";
  if (stock <= minStock) return "Low";
  return "Normal";
}

function getGarmentIcon(category) {
  switch ((category || "").toLowerCase()) {
    case "denim": return "fa-vest-patches";
    case "formal": case "formal wear": return "fa-user-tie";
    case "outerwear": return "fa-vest";
    case "ethnic wear": case "ethnic": return "fa-person";
    default: return "fa-shirt";
  }
}

function getFilteredProducts() {
  const search = (document.getElementById("productSearch")?.value || "").toLowerCase().trim();
  const category = document.getElementById("categoryFilter")?.value || "all";
  const size = document.getElementById("sizeFilter")?.value || "all";
  const status = document.getElementById("statusFilter")?.value || "all";

  return productsList.filter(p => {
    const pid = p.product_id || p.id || "";
    const pname = p.product_name || p.name || "";
    const pcat = p.category_name || p.category || "";
    const psup = p.supplier_name || p.supplier || "";
    const currentStatus = p.stock_status || p.status || calculateStockStatus(p.stock_quantity || p.stock, p.reorder_level || p.min_stock);

    const matchesSearch = !search || 
      pid.toLowerCase().includes(search) || 
      pname.toLowerCase().includes(search) || 
      psup.toLowerCase().includes(search) ||
      pcat.toLowerCase().includes(search);

    const matchesCat = category === "all" || pcat.toLowerCase() === category.toLowerCase();
    const matchesSize = size === "all" || String(p.size).toLowerCase() === size.toLowerCase();
    const matchesStatus = status === "all" || currentStatus.toLowerCase() === status.toLowerCase();

    return matchesSearch && matchesCat && matchesSize && matchesStatus;
  });
}

function renderProductsTable() {
  const tableBody = document.getElementById("productsTableBody");
  const countEl = document.getElementById("productCountBadge");
  if (!tableBody) return;

  const filtered = getFilteredProducts();
  if (countEl) countEl.textContent = `${filtered.length} items`;

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; padding: 3rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-layer-group" style="font-size: 2rem; color: var(--text-light); margin-bottom: 0.5rem; display: block;"></i>
          <strong>No matching garment products found</strong>
          <p style="font-size: 0.82rem; margin-top: 0.25rem;">Try adjusting your filters or click "Add Product" to create one.</p>
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = filtered.map(p => {
    const pid = p.product_id || p.id;
    const pname = p.product_name || p.name;
    const pcat = p.category_name || p.category;
    const psup = p.supplier_name || p.supplier;
    const stockQty = p.stock_quantity !== undefined ? p.stock_quantity : (p.stock || 0);
    const status = p.stock_status || p.status || calculateStockStatus(stockQty, p.reorder_level || p.min_stock);

    let badgeClass = "badge-success";
    if (status === "Low") badgeClass = "badge-warning";
    if (status === "Critical") badgeClass = "badge-danger";

    const icon = getGarmentIcon(pcat);

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-muted); font-size: 0.85rem;">${pid}</td>
        <td>
          <div class="table-product-cell">
            <div class="product-thumb">
              <i class="fa-solid ${icon}"></i>
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text-main);">${pname}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">SKU: FF-${pid}</div>
            </div>
          </div>
        </td>
        <td><span class="badge badge-info" style="font-weight:600;">${pcat}</span></td>
        <td style="font-weight: 600;">${p.size || "M"}</td>
        <td style="font-weight: 700; color: var(--text-main);">${formatCurrency(p.price || 0)}</td>
        <td style="color: var(--text-muted); font-weight: 500;">${psup || "N/A"}</td>
        <td style="font-weight: 700;">${stockQty} units</td>
        <td><span class="badge ${badgeClass}">${status}</span></td>
        <td>
          <div class="product-actions-group">
            <button class="action-btn-mini" title="View Details" onclick="viewProductDetails('${pid}')">
              <i class="fa-regular fa-eye"></i>
            </button>
            <button class="action-btn-mini" title="Edit Product" onclick="openEditProductModal('${pid}')">
              <i class="fa-regular fa-pen-to-square"></i>
            </button>
            <button class="action-btn-mini delete-hover" title="Delete Product" onclick="confirmDeleteProduct('${pid}')">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

async function populateSupplierSelect() {
  const select = document.getElementById("productSupplier");
  if (!select) return;

  try {
    const res = await apiRequest("/suppliers");
    const suppliers = res.data || [];
    select.innerHTML = `
      <option value="">Select a supplier...</option>
      ${suppliers.map(s => `<option value="${s.supplier_name || s.name}">${s.supplier_name || s.name}</option>`).join("")}
    `;
  } catch (e) {
    console.warn("Could not load suppliers for dropdown:", e.message);
  }
}

function setupEventListeners() {
  document.getElementById("productSearch")?.addEventListener("input", renderProductsTable);
  document.getElementById("categoryFilter")?.addEventListener("change", renderProductsTable);
  document.getElementById("sizeFilter")?.addEventListener("change", renderProductsTable);
  document.getElementById("statusFilter")?.addEventListener("change", renderProductsTable);

  const productForm = document.getElementById("productForm");
  if (productForm) {
    productForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const editId = document.getElementById("productId").value.trim();
      const name = document.getElementById("productName").value.trim();
      const category = document.getElementById("productCategory").value;
      const size = document.getElementById("productSize").value;
      const price = Number(document.getElementById("productPrice").value);
      const supplier = document.getElementById("productSupplier").value;
      const stock = Number(document.getElementById("productStock").value);
      const minStock = Number(document.getElementById("productMinStock").value) || 20;

      const isEdit = document.getElementById("isEditMode").value === "true";

      const productPayload = {
        product_id: editId || `P${String(productsList.length + 1).padStart(3, "0")}`,
        id: editId || `P${String(productsList.length + 1).padStart(3, "0")}`,
        product_name: name,
        name: name,
        category_name: category,
        category: category,
        size,
        price,
        supplier_name: supplier,
        supplier,
        stock_quantity: stock,
        stock,
        reorder_level: minStock,
        min_stock: minStock,
        minStock: minStock
      };

      if (isEdit) {
        updateProduct(editId, productPayload);
      } else {
        addProduct(productPayload);
      }

      closeModal("productModal");
    });
  }

  document.getElementById("confirmDeleteBtn")?.addEventListener("click", () => {
    if (deleteTargetId) {
      deleteProduct(deleteTargetId);
      deleteTargetId = null;
      closeModal("deleteConfirmModal");
    }
  });
}

function openAddProductModal() {
  document.getElementById("productForm").reset();
  document.getElementById("isEditMode").value = "false";
  document.getElementById("productModalTitle").textContent = "Add Garment Product";
  document.getElementById("productId").value = `P${String(productsList.length + 1).padStart(3, "0")}`;
  openModal("productModal");
}

function openEditProductModal(id) {
  const p = productsList.find(item => (item.product_id === id || item.id === id));
  if (!p) return;

  document.getElementById("isEditMode").value = "true";
  document.getElementById("productModalTitle").textContent = "Edit Garment Product";
  document.getElementById("productId").value = p.product_id || p.id;
  document.getElementById("productName").value = p.product_name || p.name;
  document.getElementById("productCategory").value = p.category_name || p.category;
  document.getElementById("productSize").value = p.size;
  document.getElementById("productPrice").value = p.price;
  document.getElementById("productSupplier").value = p.supplier_name || p.supplier;
  document.getElementById("productStock").value = p.stock_quantity !== undefined ? p.stock_quantity : p.stock;
  document.getElementById("productMinStock").value = p.reorder_level || p.min_stock || 20;

  openModal("productModal");
}

function viewProductDetails(id) {
  const p = productsList.find(item => (item.product_id === id || item.id === id));
  if (!p) return;

  const content = document.getElementById("productDetailContent");
  const pid = p.product_id || p.id;
  const pname = p.product_name || p.name;
  const pcat = p.category_name || p.category;
  const psup = p.supplier_name || p.supplier;
  const stockQty = p.stock_quantity !== undefined ? p.stock_quantity : p.stock;
  const status = p.stock_status || p.status || calculateStockStatus(stockQty, p.reorder_level || p.min_stock);
  const statusColor = status === "Normal" ? "text-success" : (status === "Low" ? "text-warning" : "text-danger");

  content.innerHTML = `
    <div style="display:flex; align-items:center; gap: 1rem; margin-bottom: 1.25rem;">
      <div class="product-thumb" style="width: 50px; height: 50px; font-size: 1.4rem;">
        <i class="fa-solid ${getGarmentIcon(pcat)}"></i>
      </div>
      <div>
        <h3 style="font-size: 1.25rem; font-weight: 800;">${pname}</h3>
        <span style="font-size: 0.85rem; color: var(--text-muted);">Product Code: ${pid} &bull; Category: ${pcat}</span>
      </div>
    </div>

    <div class="product-detail-grid">
      <div class="detail-item">
        <div class="label">Retail Price</div>
        <div class="value">${formatCurrency(p.price)}</div>
      </div>
      <div class="detail-item">
        <div class="label">Current Stock</div>
        <div class="value">${stockQty} units</div>
      </div>
      <div class="detail-item">
        <div class="label">Garment Size</div>
        <div class="value">${p.size}</div>
      </div>
      <div class="detail-item">
        <div class="label">Inventory Status</div>
        <div class="value ${statusColor}">${status}</div>
      </div>
      <div class="detail-item" style="grid-column: span 2;">
        <div class="label">Primary Supplier</div>
        <div class="value" style="font-size: 0.95rem;">${psup}</div>
      </div>
    </div>
  `;

  openModal("viewProductModal");
}

function confirmDeleteProduct(id) {
  deleteTargetId = id;
  const p = productsList.find(item => (item.product_id === id || item.id === id));
  const nameEl = document.getElementById("deleteProductName");
  if (nameEl && p) nameEl.textContent = `"${p.product_name || p.name}" (${p.product_id || p.id})`;
  openModal("deleteConfirmModal");
}
