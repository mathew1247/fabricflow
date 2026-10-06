/**
 * FABRICFLOW ANALYTICS - SUPPLIERS SCRIPT
 * Production supplier directory connected to Flask REST API /api/suppliers & Cloud Firestore
 */

let suppliersList = [];
let deleteSupplierTargetId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadSuppliers();
  setupSupplierListeners();
});

async function loadSuppliers() {
  const tbody = document.getElementById("suppliersTableBody");
  if (tbody && suppliersList.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding: 2.5rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-spinner fa-spin" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
          <span>Loading suppliers from Cloud Firestore...</span>
        </td>
      </tr>
    `;
  }

  try {
    const res = await apiRequest("/suppliers");
    suppliersList = res.data || [];
    renderSuppliersTable();
  } catch (err) {
    console.error("API load failed for suppliers:", err.message);
    showToast("Failed to load suppliers: " + err.message, "error");
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align:center; padding: 2.5rem 1rem; color: var(--danger);">
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
            <span>Error connecting to server. Please ensure backend is running.</span>
          </td>
        </tr>
      `;
    }
  }
}

async function addSupplier(supplierData) {
  try {
    await apiRequest("/suppliers", "POST", supplierData);
    showToast(`Supplier "${supplierData.supplier_name || supplierData.name}" added to Firestore!`, "success");
    await loadSuppliers();
  } catch (err) {
    console.error("API add supplier failed:", err.message);
    showToast(`Failed to add supplier: ${err.message}`, "error");
  }
}

async function updateSupplier(id, updatedData) {
  try {
    await apiRequest(`/suppliers/${id}`, "PUT", updatedData);
    showToast(`Supplier "${updatedData.supplier_name || updatedData.name}" updated successfully!`, "success");
    await loadSuppliers();
  } catch (err) {
    console.error("API update supplier failed:", err.message);
    showToast(`Failed to update supplier: ${err.message}`, "error");
  }
}

async function deleteSupplier(id) {
  try {
    await apiRequest(`/suppliers/${id}`, "DELETE");
    showToast("Supplier deleted successfully from Firestore.", "success");
    await loadSuppliers();
  } catch (err) {
    console.error("API delete supplier failed:", err.message);
    showToast(`Failed to delete supplier: ${err.message}`, "error");
  }
}

function getFilteredSuppliers() {
  const search = (document.getElementById("supplierSearch")?.value || "").toLowerCase().trim();
  const status = document.getElementById("supplierStatusFilter")?.value || "all";

  return suppliersList.filter(s => {
    const sid = s.supplier_id || s.id || "";
    const sname = s.supplier_name || s.name || "";
    const saddr = s.address || "";
    const sstatus = s.status || "Active";

    const matchesSearch = !search || 
      sid.toLowerCase().includes(search) || 
      sname.toLowerCase().includes(search) || 
      saddr.toLowerCase().includes(search);
    const matchesStatus = status === "all" || sstatus.toLowerCase() === status.toLowerCase();

    return matchesSearch && matchesStatus;
  });
}

function renderSuppliersTable() {
  const tbody = document.getElementById("suppliersTableBody");
  if (!tbody) return;

  const filtered = getFilteredSuppliers();

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding: 3rem 1rem; color: var(--text-muted);">
          <i class="fa-solid fa-truck-fast" style="font-size: 2rem; color: var(--text-light); margin-bottom: 0.5rem; display: block;"></i>
          <strong>No suppliers found in Cloud Firestore</strong>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(s => {
    const sid = s.supplier_id || s.id;
    const sname = s.supplier_name || s.name;
    const scontact = s.contact_number || s.contact;
    const isActive = String(s.status).toLowerCase() === "active";
    const badgeClass = isActive ? "badge-success" : "badge-warning";
    const prods = s.products_supplied !== undefined ? s.products_supplied : (s.productsSupplied || 6);

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-muted);">${sid}</td>
        <td>
          <div class="table-product-cell">
            <div class="supplier-avatar">
              <i class="fa-solid fa-industry"></i>
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text-main);">${sname}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">${s.email || "partner@fabricflow.com"}</div>
            </div>
          </div>
        </td>
        <td style="font-weight: 600; color: var(--text-main);">
          <i class="fa-solid fa-phone" style="font-size: 0.75rem; color: var(--text-light); margin-right: 4px;"></i>
          ${scontact}
        </td>
        <td style="color: var(--text-muted); font-size: 0.85rem; font-weight: 500;">
          <i class="fa-solid fa-location-dot" style="font-size: 0.75rem; color: var(--text-light); margin-right: 4px;"></i>
          ${s.address}
        </td>
        <td>
          <span class="badge badge-purple">${prods} Categories</span>
        </td>
        <td><span class="badge ${badgeClass}">${s.status}</span></td>
        <td>
          <div class="product-actions-group">
            <button class="action-btn-mini" title="Edit" onclick="openEditSupplierModal('${sid}')">
              <i class="fa-regular fa-pen-to-square"></i>
            </button>
            <button class="action-btn-mini delete-hover" title="Delete" onclick="confirmDeleteSupplier('${sid}')">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function openAddSupplierModal() {
  document.getElementById("supplierForm").reset();
  document.getElementById("supplierIsEdit").value = "false";
  document.getElementById("supplierModalTitle").textContent = "Add Garment Supplier";
  document.getElementById("supplierId").value = `SUP-${100 + suppliersList.length + 1}`;
  openModal("supplierModal");
}

function openEditSupplierModal(id) {
  const s = suppliersList.find(item => (item.supplier_id === id || item.id === id));
  if (!s) return;

  document.getElementById("supplierIsEdit").value = "true";
  document.getElementById("supplierModalTitle").textContent = "Edit Garment Supplier";
  document.getElementById("supplierId").value = s.supplier_id || s.id;
  document.getElementById("supplierName").value = s.supplier_name || s.name;
  document.getElementById("supplierContact").value = s.contact_number || s.contact;
  document.getElementById("supplierEmail").value = s.email || "";
  document.getElementById("supplierAddress").value = s.address;
  document.getElementById("supplierStatus").value = s.status;

  openModal("supplierModal");
}

function confirmDeleteSupplier(id) {
  deleteSupplierTargetId = id;
  const s = suppliersList.find(item => (item.supplier_id === id || item.id === id));
  const nameEl = document.getElementById("deleteSupplierName");
  if (nameEl && s) nameEl.textContent = `"${s.supplier_name || s.name}" (${s.supplier_id || s.id})`;
  openModal("deleteSupplierModal");
}

function setupSupplierListeners() {
  document.getElementById("supplierSearch")?.addEventListener("input", renderSuppliersTable);
  document.getElementById("supplierStatusFilter")?.addEventListener("change", renderSuppliersTable);

  document.getElementById("supplierForm")?.addEventListener("submit", (e) => {
    e.preventDefault();

    const id = document.getElementById("supplierId").value.trim();
    const name = document.getElementById("supplierName").value.trim();
    const contact = document.getElementById("supplierContact").value.trim();
    const email = document.getElementById("supplierEmail").value.trim();
    const address = document.getElementById("supplierAddress").value.trim();
    const status = document.getElementById("supplierStatus").value;

    const isEdit = document.getElementById("supplierIsEdit").value === "true";

    const supplierPayload = {
      supplier_id: id,
      id: id,
      supplier_name: name,
      name: name,
      contact_number: contact,
      contact: contact,
      email,
      address,
      products_supplied: 10,
      productsSupplied: 10,
      status
    };

    if (isEdit) {
      updateSupplier(id, supplierPayload);
    } else {
      addSupplier(supplierPayload);
    }

    closeModal("supplierModal");
  });

  document.getElementById("confirmDeleteSupplierBtn")?.addEventListener("click", () => {
    if (deleteSupplierTargetId) {
      deleteSupplier(deleteSupplierTargetId);
      deleteSupplierTargetId = null;
      closeModal("deleteSupplierModal");
    }
  });
}
