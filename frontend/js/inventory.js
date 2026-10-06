/**
 * FABRICFLOW ANALYTICS - INVENTORY SCRIPT
 * Production stock management connected to Flask REST API /api/inventory & Firestore
 */

let inventoryItems = [];
let currentAdjustTarget = null;

document.addEventListener("DOMContentLoaded", () => {
  loadInventory();
  setupInventoryListeners();
});

async function loadInventory() {
  const tbody = document.getElementById("inventoryTableBody");
  if (tbody && inventoryItems.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center; padding: 2.5rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-spinner fa-spin" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
          <span>Loading inventory from Cloud Firestore...</span>
        </td>
      </tr>
    `;
  }

  try {
    const [invRes, summaryRes] = await Promise.all([
      apiRequest("/inventory"),
      apiRequest("/inventory/summary")
    ]);
    inventoryItems = invRes.data || [];
    renderInventorySummaryFromAPI(summaryRes.data);
    renderInventoryTable();
  } catch (err) {
    console.error("API load failed for inventory:", err.message);
    showToast("Failed to load inventory: " + err.message, "error");
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align:center; padding: 2.5rem 1rem; color: var(--danger);">
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
            <span>Error connecting to server. Please ensure backend is running.</span>
          </td>
        </tr>
      `;
    }
  }
}

async function adjustStock(productId, updatedStock, adjType = "set", qty = 0, reason = "") {
  try {
    const res = await apiRequest(`/inventory/${productId}/adjust`, "POST", {
      type: adjType,
      quantity: qty || updatedStock,
      reason: reason
    });

    const updated = res.data;
    showToast(`Stock successfully updated in Firestore for ${updated?.product_name || updated?.name || productId} to ${updatedStock} units.`, "success");
    await loadInventory();
  } catch (err) {
    console.error("API adjustment failed:", err.message);
    showToast(`Adjustment failed: ${err.message}`, "error");
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

function renderInventorySummaryFromAPI(summary) {
  if (!summary) return;
  const totalEl = document.getElementById("invTotalStock");
  const normEl = document.getElementById("invNormalStock");
  const lowEl = document.getElementById("invLowStock");
  const critEl = document.getElementById("invCriticalStock");

  if (totalEl) totalEl.textContent = Number(summary.total_stock_units || 0).toLocaleString();
  if (normEl) normEl.textContent = Number(summary.normal_units || 0).toLocaleString();
  if (lowEl) lowEl.textContent = Number(summary.low_units || 0).toLocaleString();
  if (critEl) critEl.textContent = Number(summary.critical_units || 0).toLocaleString();
}

function getFilteredInventory() {
  const search = (document.getElementById("invSearch")?.value || "").toLowerCase().trim();
  const category = document.getElementById("invCategoryFilter")?.value || "all";
  const status = document.getElementById("invStatusFilter")?.value || "all";

  return inventoryItems.filter(p => {
    const pid = p.product_id || p.id || "";
    const pname = p.product_name || p.name || "";
    const pcat = p.category_name || p.category || "";
    const currentStatus = p.stock_status || p.status || calculateStockStatus(p.stock_quantity || p.stock, p.reorder_level || p.min_stock);

    const matchesSearch = !search || 
      pid.toLowerCase().includes(search) || 
      pname.toLowerCase().includes(search) ||
      pcat.toLowerCase().includes(search);
    const matchesCat = category === "all" || pcat.toLowerCase() === category.toLowerCase();
    const matchesStatus = status === "all" || currentStatus.toLowerCase() === status.toLowerCase();

    return matchesSearch && matchesCat && matchesStatus;
  });
}

function renderInventoryTable() {
  const tbody = document.getElementById("inventoryTableBody");
  if (!tbody) return;

  const filtered = getFilteredInventory();

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center; padding: 3rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-boxes-stacked" style="font-size: 2rem; color: var(--text-light); margin-bottom: 0.5rem; display: block;"></i>
          <strong>No stock entries found in Cloud Firestore</strong>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(p => {
    const pid = p.product_id || p.id;
    const pname = p.product_name || p.name;
    const pcat = p.category_name || p.category;
    const stockQty = p.stock_quantity !== undefined ? p.stock_quantity : (p.stock || 0);
    const reorder = p.reorder_level || p.min_stock || 20;
    const status = p.stock_status || p.status || calculateStockStatus(stockQty, reorder);

    let badgeClass = "badge-success";
    if (status === "Low") badgeClass = "badge-warning";
    if (status === "Critical") badgeClass = "badge-danger";

    const lastUpdated = p.last_updated ? p.last_updated.split("T")[0] : new Date().toISOString().split("T")[0];

    return `
      <tr>
        <td>
          <div class="table-product-cell">
            <div class="product-thumb">
              <i class="fa-solid ${getGarmentIcon(pcat)}"></i>
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text-main);">${pname}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">SKU: FF-${pid}</div>
            </div>
          </div>
        </td>
        <td><span class="badge badge-info">${pcat}</span></td>
        <td style="font-weight: 600;">${p.size || "M"}</td>
        <td>
          <span style="font-weight: 800; font-size: 0.95rem; color: var(--text-main);">${stockQty}</span>
          <span style="font-size: 0.78rem; color: var(--text-muted);"> pcs</span>
        </td>
        <td style="color: var(--text-muted); font-weight: 600;">${reorder} pcs</td>
        <td><span class="badge ${badgeClass}">${status}</span></td>
        <td style="color: var(--text-muted); font-size: 0.82rem;">${lastUpdated}</td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="openAdjustStockModal('${pid}')">
            <i class="fa-solid fa-sliders"></i>
            <span>Adjust</span>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function openAdjustStockModal(id) {
  const p = inventoryItems.find(item => (item.product_id === id || item.id === id));
  if (!p) return;

  currentAdjustTarget = p;
  const pid = p.product_id || p.id;
  const pname = p.product_name || p.name;
  const stockQty = p.stock_quantity !== undefined ? p.stock_quantity : (p.stock || 0);

  document.getElementById("adjustProductName").textContent = `${pname} (${pid})`;
  document.getElementById("adjustCurrentStock").textContent = stockQty;
  document.getElementById("adjustQty").value = 10;
  document.getElementById("adjustType").value = "add";
  document.getElementById("adjustReason").value = "Restocked from supplier";

  calculateAdjustmentPreview();
  openModal("adjustStockModal");
}

function calculateAdjustmentPreview() {
  if (!currentAdjustTarget) return;

  const current = currentAdjustTarget.stock_quantity !== undefined ? currentAdjustTarget.stock_quantity : currentAdjustTarget.stock;
  const type = document.getElementById("adjustType").value;
  const qty = parseInt(document.getElementById("adjustQty").value) || 0;

  let finalStock = current;
  if (type === "add") {
    finalStock = current + qty;
    document.getElementById("previewOp").textContent = "+";
  } else if (type === "deduct") {
    finalStock = Math.max(0, current - qty);
    document.getElementById("previewOp").textContent = "-";
  } else {
    finalStock = Math.max(0, qty);
    document.getElementById("previewOp").textContent = "=";
  }

  document.getElementById("previewCurrent").textContent = current;
  document.getElementById("previewChange").textContent = qty;
  document.getElementById("previewFinal").textContent = finalStock;
}

function setupInventoryListeners() {
  document.getElementById("invSearch")?.addEventListener("input", renderInventoryTable);
  document.getElementById("invCategoryFilter")?.addEventListener("change", renderInventoryTable);
  document.getElementById("invStatusFilter")?.addEventListener("change", renderInventoryTable);

  document.getElementById("adjustType")?.addEventListener("change", calculateAdjustmentPreview);
  document.getElementById("adjustQty")?.addEventListener("input", calculateAdjustmentPreview);

  document.getElementById("adjustStockForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!currentAdjustTarget) return;

    const finalStock = parseInt(document.getElementById("previewFinal").textContent) || 0;
    const type = document.getElementById("adjustType").value;
    const qty = parseInt(document.getElementById("adjustQty").value) || 0;
    const reason = document.getElementById("adjustReason").value;

    const pid = currentAdjustTarget.product_id || currentAdjustTarget.id;
    adjustStock(pid, finalStock, type, qty, reason);
    closeModal("adjustStockModal");
  });
}
