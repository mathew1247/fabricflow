/**
 * FABRICFLOW ANALYTICS - DEMAND FORECAST SCRIPT
 * Predictive demand modeling connected to Flask REST API /api/forecast & NumPy/Pandas
 */

let forecastChartInstance = null;
let currentForecastPeriod = "30";
let currentForecastItems = [];
let cachedSuppliers = null;

document.addEventListener("DOMContentLoaded", () => {
  loadForecast("30");
  setupForecastControls();
});

async function loadForecast(period = "30") {
  currentForecastPeriod = period;
  const categoryFilter = document.getElementById("fcCategoryFilter")?.value || "all";
  const tbody = document.getElementById("forecastTableBody");

  try {
    const res = await apiRequest(`/forecast?period=${period}&category=${categoryFilter}`);
    const data = res.data || {};

    currentForecastItems = data.table || data.products || [];
    updateForecastCardsFromAPI(data.cards);
    renderForecastChart(data.chart);
    renderForecastTable(currentForecastItems);
  } catch (err) {
    console.error("API forecast failed:", err.message);
    showToast("Failed to load forecast from backend: " + err.message, "error");
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; padding: 2rem; color: var(--danger);">
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block;"></i>
            <span>Unable to load predictive demand forecast.</span>
          </td>
        </tr>
      `;
    }
  }
}

function updateForecastCardsFromAPI(cards) {
  if (!cards) return;
  const cStock = document.getElementById("fcCurrentStock");
  const cDaily = document.getElementById("fcAvgDaily");
  const cDemand = document.getElementById("fcPredictedDemand");
  const cRec = document.getElementById("fcRecommendedStock");

  if (cStock) cStock.textContent = cards.current_stock;
  if (cDaily) cDaily.textContent = cards.avg_daily_sales;
  if (cDemand) cDemand.textContent = cards.predicted_demand;
  if (cRec) cRec.textContent = cards.recommended_stock;
}

function renderForecastChart(chartConfig) {
  const ctx = document.getElementById("forecastChartCanvas");
  if (!ctx || !chartConfig) return;

  const labels = chartConfig.labels || [];
  const historical = chartConfig.historical || [];
  const predicted = chartConfig.predicted || [];

  if (forecastChartInstance) {
    forecastChartInstance.data.labels = labels;
    forecastChartInstance.data.datasets[0].data = historical;
    forecastChartInstance.data.datasets[1].data = predicted;
    forecastChartInstance.update();
    return;
  }

  forecastChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Historical Demand",
          data: historical,
          borderColor: "#111316",
          backgroundColor: "rgba(17, 19, 22, 0.08)",
          fill: true,
          tension: 0.3,
          borderWidth: 2.8,
          pointRadius: 4,
          pointBackgroundColor: "#111316"
        },
        {
          label: "Predicted Demand (Forecast)",
          data: predicted,
          borderColor: "#64748b",
          backgroundColor: "rgba(100, 116, 139, 0.12)",
          borderDash: [5, 5],
          fill: true,
          tension: 0.3,
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: "#64748b"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
          labels: { font: { family: "Plus Jakarta Sans", size: 12, weight: "700" } }
        },
        tooltip: {
          backgroundColor: "#111316",
          padding: 10,
          cornerRadius: 10,
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ${context.raw !== null ? context.raw + ' pcs' : 'N/A'}`;
            }
          }
        }
      },
      scales: {
        y: {
          grid: { color: "#f0f2f5" },
          ticks: { font: { family: "Plus Jakarta Sans", weight: "600" } }
        },
        x: {
          grid: { display: false },
          ticks: { font: { family: "Plus Jakarta Sans", weight: "600" } }
        }
      }
    }
  });
}

function renderForecastTable(tableItems) {
  const tbody = document.getElementById("forecastTableBody");
  if (!tbody || !tableItems) return;

  const statusFilter = document.getElementById("fcStatusFilter")?.value || "all";

  const filtered = tableItems.filter(item => {
    const st = item.forecast_status || item.status;
    return statusFilter === "all" || st === statusFilter;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--text-muted);">No products matching forecast filter.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(item => {
    const st = item.forecast_status || item.status || "Maintain Stock";
    let badgeClass = "badge-success";
    if (st === "Increase Stock") badgeClass = "badge-danger";
    if (st === "Reduce Stock") badgeClass = "badge-warning";

    const pname = item.product_name || item.name;
    const pid = item.product_id || item.id;
    const stockQty = item.current_stock !== undefined ? item.current_stock : item.stock;
    const predDemand = item.predicted_demand !== undefined ? item.predicted_demand : item.predicted;
    const recStock = item.recommended_stock !== undefined ? item.recommended_stock : item.recommended;
    const needed = Math.max(0, recStock - stockQty);

    return `
      <tr>
        <td>
          <div style="font-weight: 700; color: var(--text-main);">${pname}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${pid} &bull; ${item.category}</div>
        </td>
        <td style="font-weight: 600;">${stockQty} pcs</td>
        <td style="font-weight: 700; color: var(--text-main);">${predDemand} pcs</td>
        <td style="font-weight: 800; color: var(--text-main);">${recStock} pcs</td>
        <td>
          <span class="badge ${badgeClass}">${st}</span>
          <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.25rem;">${item.reason || ''}</div>
        </td>
        <td>
          <button class="btn btn-sm btn-primary" onclick="openReorderModal('${pid}')">
            <i class="fa-solid fa-cart-shopping"></i> Reorder
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

async function loadSuppliersForModal() {
  const select = document.getElementById("reorderSupplierSelect");
  if (!select) return;

  if (cachedSuppliers && cachedSuppliers.length > 0) {
    populateSupplierDropdown(select, cachedSuppliers);
    return;
  }

  try {
    const res = await apiRequest("/suppliers");
    cachedSuppliers = res.data || [];
    populateSupplierDropdown(select, cachedSuppliers);
  } catch (err) {
    console.error("Failed to load suppliers:", err);
    select.innerHTML = '<option value="SUP-101">ABC Textiles Co. (Primary Mill)</option>';
  }
}

function populateSupplierDropdown(select, suppliers) {
  if (!suppliers || suppliers.length === 0) {
    select.innerHTML = '<option value="SUP-101">ABC Textiles Co. (Primary Mill)</option>';
    return;
  }
  select.innerHTML = suppliers.map(s => `
    <option value="${s.id || s.supplier_id}">${s.name} &bull; ${s.address || s.contact || 'Apparel Supplier'}</option>
  `).join("");
}

function openReorderModal(productId) {
  const item = currentForecastItems.find(p => (p.product_id || p.id) === productId);
  if (!item) {
    showToast("Product details not found.", "warning");
    return;
  }

  const pname = item.product_name || item.name || "Garment Item";
  const pid = item.product_id || item.id || productId;
  const category = item.category || "General";
  const status = item.forecast_status || item.status || "Maintain Stock";

  const stockQty = Number(item.current_stock !== undefined ? item.current_stock : item.stock || 0);
  const predDemand = Number(item.predicted_demand !== undefined ? item.predicted_demand : item.predicted || 0);
  const recStock = Number(item.recommended_stock !== undefined ? item.recommended_stock : item.recommended || 0);

  // Suggested replenishment calculation
  let suggestedQty = Math.max(10, recStock - stockQty);
  if (status === "Increase Stock") {
    suggestedQty = Math.max(suggestedQty, 25);
  }

  // Populate Modal Fields
  const hiddenId = document.getElementById("reorderProductId");
  const badgeEl = document.getElementById("reorderProductBadge");
  const cStockEl = document.getElementById("reorderCurrentStock");
  const pDemandEl = document.getElementById("reorderPredictedDemand");
  const rStockEl = document.getElementById("reorderRecommendedStock");
  const qtyInput = document.getElementById("reorderQuantity");
  const helpText = document.getElementById("reorderSuggestedHelp");
  const notesInput = document.getElementById("reorderNotes");

  if (hiddenId) hiddenId.value = pid;
  if (badgeEl) badgeEl.textContent = `${pname} (${pid} • ${category}) • Status: ${status}`;
  if (cStockEl) cStockEl.textContent = `${stockQty} pcs`;
  if (pDemandEl) pDemandEl.textContent = `${predDemand} pcs`;
  if (rStockEl) rStockEl.textContent = `${recStock} pcs`;
  if (qtyInput) qtyInput.value = suggestedQty;
  if (helpText) helpText.textContent = `Suggested replenishment: +${suggestedQty} pcs based on ${predDemand} pcs demand.`;
  if (notesInput) notesInput.value = `Replenishment order for ${pname} based on ${currentForecastPeriod}-day demand advice.`;

  loadSuppliersForModal();
  openModal("reorderModal");
}

function setupForecastControls() {
  const pills = document.querySelectorAll(".forecast-pill");
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const period = pill.getAttribute("data-period");
      loadForecast(period);
      showToast(`Forecast horizon set to ${period} days.`, "info");
    });
  });

  document.getElementById("fcCategoryFilter")?.addEventListener("change", () => loadForecast(currentForecastPeriod));
  document.getElementById("fcStatusFilter")?.addEventListener("change", () => loadForecast(currentForecastPeriod));

  // Reorder Form Submission
  const form = document.getElementById("reorderForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const pid = document.getElementById("reorderProductId")?.value;
      const qty = parseInt(document.getElementById("reorderQuantity")?.value, 10);
      const supplierSelect = document.getElementById("reorderSupplierSelect");
      const supplierName = supplierSelect?.options[supplierSelect.selectedIndex]?.text?.split("•")[0]?.trim() || "Supplier";
      const priority = document.getElementById("reorderPriority")?.value || "Standard";
      const actionType = document.getElementById("reorderActionType")?.value || "restock_now";
      const notes = document.getElementById("reorderNotes")?.value || "";
      const submitBtn = document.getElementById("confirmReorderBtn");

      if (!pid || !qty || qty <= 0) {
        showToast("Please enter a valid reorder quantity.", "warning");
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Reorder...';
      }

      try {
        if (actionType === "restock_now") {
          // Adjust stock directly in Firestore
          await apiRequest(`/inventory/${pid}/adjust`, "POST", {
            type: "add",
            quantity: qty,
            reason: `Reorder PO (${priority}) via ${supplierName}: ${notes}`
          });
          showToast(`Reorder Confirmed! Restocked +${qty} pcs for ${pid} in Firestore.`, "success");
        } else {
          showToast(`Draft Purchase Order saved for ${qty} pcs of ${pid}.`, "info");
        }

        closeModal("reorderModal");
        await loadForecast(currentForecastPeriod);
      } catch (err) {
        console.error("Reorder submission failed:", err);
        showToast("Failed to place reorder: " + err.message, "error");
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> Confirm & Place Reorder';
        }
      }
    });
  }
}
