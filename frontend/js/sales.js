/**
 * FABRICFLOW ANALYTICS - SALES MANAGEMENT SCRIPT
 * Production sales recorder connected to Flask REST API /api/sales & Cloud Firestore atomic inventory reduction
 */

let salesList = [];
let availableProducts = [];

document.addEventListener("DOMContentLoaded", () => {
  loadSales();
  setupSalesListeners();
});

async function loadSales() {
  const tbody = document.getElementById("salesTableBody");
  if (tbody && salesList.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; padding: 2.5rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-spinner fa-spin" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
          <span>Loading sales transactions from Cloud Firestore...</span>
        </td>
      </tr>
    `;
  }

  try {
    const [salesRes, prodRes] = await Promise.all([
      apiRequest("/sales"),
      apiRequest("/products")
    ]);
    salesList = salesRes.data || [];
    availableProducts = prodRes.data || [];
    populateProductSelect();
    renderSalesTable();
  } catch (err) {
    console.error("API load failed for sales:", err.message);
    showToast("Failed to load sales: " + err.message, "error");
    if (tbody) {
      tbody.innerHTML = `
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

async function recordSale(saleData) {
  try {
    const res = await apiRequest("/sales", "POST", saleData);
    const recorded = res.data || saleData;
    const totalAmount = recorded.total_amount || recorded.total || saleData.total || 0;
    showToast(`Sale recorded successfully in Firestore! Total: ${formatCurrency(totalAmount)}`, "success");
    await loadSales();
  } catch (err) {
    console.error("API record sale failed:", err.message);
    showToast(`Failed to record sale: ${err.message}`, "error");
  }
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

function populateProductSelect() {
  const select = document.getElementById("saleProductSelect");
  if (!select) return;

  select.innerHTML = `
    <option value="">Select garment product...</option>
    ${availableProducts.map(p => {
      const pid = p.product_id || p.id;
      const pname = p.product_name || p.name;
      const pcat = p.category_name || p.category;
      const stockQty = p.stock_quantity !== undefined ? p.stock_quantity : (p.stock || 0);
      return `
        <option value="${pid}" data-name="${pname}" data-price="${p.price}" data-category="${pcat}" data-stock="${stockQty}">
          ${pname} (${pcat} - Size ${p.size || 'M'}) [Stock: ${stockQty}]
        </option>
      `;
    }).join("")}
  `;
}

function getFilteredSales() {
  const search = (document.getElementById("saleSearch")?.value || "").toLowerCase().trim();
  const category = document.getElementById("saleCategoryFilter")?.value || "all";
  const status = document.getElementById("saleStatusFilter")?.value || "all";

  return salesList.filter(s => {
    const sid = s.sale_id || s.id || "";
    const prod = s.product_name || s.product || "";
    const cat = s.category_name || s.category || "";

    const matchesSearch = !search || 
      sid.toLowerCase().includes(search) || 
      prod.toLowerCase().includes(search);
    const matchesCat = category === "all" || cat.toLowerCase() === category.toLowerCase();
    const matchesStatus = status === "all" || s.status.toLowerCase() === status.toLowerCase();

    return matchesSearch && matchesCat && matchesStatus;
  });
}

function renderSalesTable() {
  const tbody = document.getElementById("salesTableBody");
  if (!tbody) return;

  const filtered = getFilteredSales();

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; padding: 3rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-cart-shopping" style="font-size: 2rem; color: var(--text-light); margin-bottom: 0.5rem; display: block;"></i>
          <strong>No sales transactions found in Cloud Firestore</strong>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(s => {
    const isCompleted = String(s.status).toLowerCase() === "completed";
    const badgeClass = isCompleted ? "badge-success" : "badge-warning";
    const cat = s.category_name || s.category || "General";
    const icon = getGarmentIcon(cat);
    const unitPrice = s.unit_price !== undefined ? s.unit_price : (s.unitPrice || 0);
    const total = s.total_amount !== undefined ? s.total_amount : (s.total || s.quantity * unitPrice);
    const sid = s.sale_id || s.id;
    const prodName = s.product_name || s.product;
    const saleDate = s.sale_date || s.date;

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-muted); font-size: 0.85rem;">${sid}</td>
        <td>
          <div class="table-product-cell">
            <div class="garment-avatar">
              <i class="fa-solid ${icon}"></i>
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text-main);">${prodName}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">Garment Item</div>
            </div>
          </div>
        </td>
        <td><span class="badge badge-info">${cat}</span></td>
        <td style="font-weight: 700;">${s.quantity} pcs</td>
        <td style="color: var(--text-muted); font-weight: 500;">${formatCurrency(unitPrice)}</td>
        <td style="font-weight: 800; color: var(--text-main);">${formatCurrency(total)}</td>
        <td style="color: var(--text-muted); font-size: 0.82rem; font-weight: 500;">${saleDate}</td>
        <td><span class="badge ${badgeClass}">${s.status}</span></td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="viewSaleReceipt('${sid}')">
            <i class="fa-solid fa-receipt"></i>
            <span>Invoice</span>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function updateStockImpactAndTotal() {
  const select = document.getElementById("saleProductSelect");
  const selectedOption = select.options[select.selectedIndex];
  const qtyInput = document.getElementById("saleQty");
  const priceInput = document.getElementById("saleUnitPrice");

  if (!selectedOption || !selectedOption.value) {
    document.getElementById("impactCurrent").textContent = "0";
    document.getElementById("impactQty").textContent = "0";
    document.getElementById("impactRemain").textContent = "0";
    document.getElementById("saleTotal").value = "₹0";
    return;
  }

  const currentStock = parseInt(selectedOption.getAttribute("data-stock")) || 0;
  const defaultPrice = parseFloat(selectedOption.getAttribute("data-price")) || 0;

  if (!priceInput.value) {
    priceInput.value = defaultPrice;
  }

  const unitPrice = parseFloat(priceInput.value) || 0;
  const qty = parseInt(qtyInput.value) || 0;
  const total = qty * unitPrice;
  const remaining = Math.max(0, currentStock - qty);

  document.getElementById("impactCurrent").textContent = currentStock;
  document.getElementById("impactQty").textContent = qty;
  document.getElementById("impactRemain").textContent = remaining;
  document.getElementById("saleTotal").value = formatCurrency(total);
}

function openRecordSaleModal() {
  document.getElementById("saleForm").reset();
  document.getElementById("saleDate").value = new Date().toISOString().split("T")[0];
  populateProductSelect();
  updateStockImpactAndTotal();
  openModal("recordSaleModal");
}

function viewSaleReceipt(id) {
  const sale = salesList.find(s => (s.sale_id === id || s.id === id));
  if (!sale) return;

  const unitPrice = sale.unit_price !== undefined ? sale.unit_price : (sale.unitPrice || 0);
  const total = sale.total_amount !== undefined ? sale.total_amount : (sale.total || sale.quantity * unitPrice);
  const sid = sale.sale_id || sale.id;
  const prodName = sale.product_name || sale.product;
  const cat = sale.category_name || sale.category;
  const sdate = sale.sale_date || sale.date;

  const content = document.getElementById("receiptModalContent");
  content.innerHTML = `
    <div style="text-align: center; border-bottom: 1px dashed var(--border-color); padding-bottom: 1rem; margin-bottom: 1rem;">
      <h3 style="font-size: 1.25rem; font-weight: 800;">FabricFlow Store Receipt</h3>
      <p style="font-size: 0.8rem; color: var(--text-muted);">Sale Invoice #${sid} &bull; ${sdate}</p>
    </div>

    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem;">
      <span style="color: var(--text-muted);">Product:</span>
      <strong>${prodName} (${cat})</strong>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem;">
      <span style="color: var(--text-muted);">Quantity:</span>
      <strong>${sale.quantity} units</strong>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem;">
      <span style="color: var(--text-muted);">Unit Price:</span>
      <strong>${formatCurrency(unitPrice)}</strong>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; font-size: 0.9rem;">
      <span style="color: var(--text-muted);">Status:</span>
      <span class="badge ${String(sale.status).toLowerCase() === 'completed' ? 'badge-success' : 'badge-warning'}">${sale.status}</span>
    </div>

    <div style="display: flex; justify-content: space-between; border-top: 1px solid var(--border-color); padding-top: 0.75rem; font-size: 1.15rem; font-weight: 800;">
      <span>Total Paid:</span>
      <span class="text-primary">${formatCurrency(total)}</span>
    </div>
  `;

  openModal("receiptModal");
}

function setupSalesListeners() {
  document.getElementById("saleSearch")?.addEventListener("input", renderSalesTable);
  document.getElementById("saleCategoryFilter")?.addEventListener("change", renderSalesTable);
  document.getElementById("saleStatusFilter")?.addEventListener("change", renderSalesTable);

  document.getElementById("saleProductSelect")?.addEventListener("change", () => {
    const select = document.getElementById("saleProductSelect");
    const selectedOption = select.options[select.selectedIndex];
    if (selectedOption && selectedOption.value) {
      document.getElementById("saleUnitPrice").value = selectedOption.getAttribute("data-price") || "899";
    }
    updateStockImpactAndTotal();
  });

  document.getElementById("saleQty")?.addEventListener("input", updateStockImpactAndTotal);
  document.getElementById("saleUnitPrice")?.addEventListener("input", updateStockImpactAndTotal);

  document.getElementById("saleForm")?.addEventListener("submit", (e) => {
    e.preventDefault();

    const select = document.getElementById("saleProductSelect");
    const selectedOption = select.options[select.selectedIndex];
    if (!selectedOption || !selectedOption.value) {
      showToast("Please select a valid garment product.", "warning");
      return;
    }

    const productId = selectedOption.value;
    const productName = selectedOption.getAttribute("data-name") || "Garment Item";
    const category = selectedOption.getAttribute("data-category") || "Casual";
    const qty = parseInt(document.getElementById("saleQty").value) || 1;
    const unitPrice = parseFloat(document.getElementById("saleUnitPrice").value) || 0;
    const date = document.getElementById("saleDate").value;
    const status = document.getElementById("saleStatus").value;

    const newSale = {
      product_id: productId,
      product_name: productName,
      product: productName,
      category_name: category,
      category: category,
      quantity: qty,
      unit_price: unitPrice,
      unitPrice: unitPrice,
      total_amount: qty * unitPrice,
      total: qty * unitPrice,
      sale_date: date,
      date: date,
      status: status
    };

    recordSale(newSale);
    closeModal("recordSaleModal");
  });
}
