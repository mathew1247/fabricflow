/**
 * FABRICFLOW ANALYTICS - DASHBOARD SCRIPT
 * Connects to Flask REST API /api/dashboard and renders real Cloud Firestore data with Chart.js
 */

let salesTrendChartInstance = null;
let stockDonutChartInstance = null;

let currentPeriod = "monthly";
let currentStartDate = "2024-09-01";
let currentEndDate = "2024-09-30";

document.addEventListener("DOMContentLoaded", () => {
  initToolbarControls();
  loadDashboardData(currentPeriod, currentStartDate, currentEndDate);

  // Periodic subtle background refresh every 60 seconds without heavy polling
  setInterval(() => {
    loadDashboardData(currentPeriod, currentStartDate, currentEndDate, true);
  }, 60000);
});

function initToolbarControls() {
  const pills = document.querySelectorAll("#dashboardTimePills .time-pill");
  const trendFilter = document.getElementById("trendFilterSelect");
  const datePickerBtn = document.getElementById("dateRangePicker");
  const dateDropdown = document.getElementById("dateRangeDropdown");
  const dateArrow = document.getElementById("datePickerArrow");
  const presetBtns = document.querySelectorAll("#datePresetsGrid .date-preset-btn");
  const applyCustomBtn = document.getElementById("applyCustomDateRangeBtn");
  const resetBtn = document.getElementById("resetDateRangeBtn");
  const customStart = document.getElementById("customStartDate");
  const customEnd = document.getElementById("customEndDate");

  // 1. Time Pill buttons (Day, Week, Month, Year)
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const pVal = pill.getAttribute("data-period");

      if (pVal === "day") {
        currentPeriod = "daily";
        currentStartDate = "2024-10-06";
        currentEndDate = "2024-10-06";
      } else if (pVal === "week") {
        currentPeriod = "weekly";
        currentStartDate = "2024-09-30";
        currentEndDate = "2024-10-06";
      } else if (pVal === "year") {
        currentPeriod = "yearly";
        currentStartDate = "2024-01-01";
        currentEndDate = "2024-12-31";
      } else { // month
        currentPeriod = "monthly";
        currentStartDate = "2024-09-01";
        currentEndDate = "2024-09-30";
      }

      if (trendFilter) {
        trendFilter.value = currentPeriod;
      }

      if (customStart && currentStartDate) customStart.value = currentStartDate;
      if (customEnd && currentEndDate) customEnd.value = currentEndDate;

      loadDashboardData(currentPeriod, currentStartDate, currentEndDate);
    });
  });

  // 2. Trend Filter Select dropdown sync
  if (trendFilter) {
    trendFilter.addEventListener("change", (e) => {
      currentPeriod = e.target.value;
      if (currentPeriod === "daily") {
        currentStartDate = "2024-10-06";
        currentEndDate = "2024-10-06";
      } else if (currentPeriod === "weekly") {
        currentStartDate = "2024-09-30";
        currentEndDate = "2024-10-06";
      } else if (currentPeriod === "yearly") {
        currentStartDate = "2024-01-01";
        currentEndDate = "2024-12-31";
      } else {
        currentStartDate = "2024-09-01";
        currentEndDate = "2024-09-30";
      }

      pills.forEach(p => {
        const pVal = p.getAttribute("data-period");
        if ((currentPeriod === "daily" && pVal === "day") ||
            (currentPeriod === "weekly" && pVal === "week") ||
            (currentPeriod === "monthly" && pVal === "month") ||
            (currentPeriod === "yearly" && pVal === "year")) {
          p.classList.add("active");
        } else {
          p.classList.remove("active");
        }
      });

      loadDashboardData(currentPeriod, currentStartDate, currentEndDate);
    });
  }

  // 3. Toggle Date Range Popover
  if (datePickerBtn && dateDropdown) {
    datePickerBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isVisible = dateDropdown.style.display === "flex";
      dateDropdown.style.display = isVisible ? "none" : "flex";
      if (dateArrow) {
        dateArrow.style.transform = isVisible ? "rotate(0deg)" : "rotate(180deg)";
      }
    });

    dateDropdown.addEventListener("click", (e) => {
      e.stopPropagation();
    });

    document.addEventListener("click", () => {
      dateDropdown.style.display = "none";
      if (dateArrow) dateArrow.style.transform = "rotate(0deg)";
    });
  }

  // 4. Preset Buttons
  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      presetBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      currentStartDate = btn.getAttribute("data-start") || "";
      currentEndDate = btn.getAttribute("data-end") || "";

      if (customStart && currentStartDate) customStart.value = currentStartDate;
      if (customEnd && currentEndDate) customEnd.value = currentEndDate;

      if (dateDropdown) dateDropdown.style.display = "none";
      if (dateArrow) dateArrow.style.transform = "rotate(0deg)";

      loadDashboardData(currentPeriod, currentStartDate, currentEndDate);
      showToast(`Filter applied: ${btn.textContent.trim()}`, "info");
    });
  });

  // 5. Apply Custom Date Range Button
  if (applyCustomBtn && customStart && customEnd) {
    applyCustomBtn.addEventListener("click", () => {
      const sVal = customStart.value;
      const eVal = customEnd.value;
      if (sVal && eVal && sVal > eVal) {
        showToast("Start date cannot be after end date", "warning");
        return;
      }
      presetBtns.forEach(b => b.classList.remove("active"));
      currentStartDate = sVal;
      currentEndDate = eVal;

      if (dateDropdown) dateDropdown.style.display = "none";
      if (dateArrow) dateArrow.style.transform = "rotate(0deg)";

      loadDashboardData(currentPeriod, currentStartDate, currentEndDate);
      showToast("Custom date range applied", "info");
    });
  }

  // 6. Reset Button
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      presetBtns.forEach(b => b.classList.remove("active"));
      const defaultPreset = document.querySelector('[data-preset="sep"]');
      if (defaultPreset) defaultPreset.classList.add("active");

      currentPeriod = "monthly";
      currentStartDate = "2024-09-01";
      currentEndDate = "2024-09-30";
      if (customStart) customStart.value = currentStartDate;
      if (customEnd) customEnd.value = currentEndDate;

      pills.forEach(p => {
        if (p.getAttribute("data-period") === "month") p.classList.add("active");
        else p.classList.remove("active");
      });

      if (dateDropdown) dateDropdown.style.display = "none";
      if (dateArrow) dateArrow.style.transform = "rotate(0deg)";

      loadDashboardData(currentPeriod, currentStartDate, currentEndDate);
      showToast("Date filter reset to Sep 2024", "info");
    });
  }
}

async function loadDashboardData(period = "monthly", startDate = "", endDate = "", isSilent = false) {
  try {
    let url = `/dashboard?period=${encodeURIComponent(period)}`;
    if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`;
    if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`;

    const res = await apiRequest(url);
    const data = res.data || {};

    // Update Date Range Button Text
    const dateSpan = document.getElementById("dateRangeSpan");
    if (dateSpan && data.date_range?.display) {
      dateSpan.textContent = data.date_range.display;
    }

    renderKPIs(data);
    renderSalesTrendChart(data.sales_trend);
    renderStockDonutChart(data.stock_status);
    renderTopCategories(data.top_categories);
    renderRecentSalesTable(data.recent_sales);

    if (!isSilent && window.location.hash === "#refresh") {
      showToast("Dashboard metrics refreshed from Firestore.", "info");
    }
  } catch (err) {
    console.error("Failed to load dashboard data from Flask API:", err.message);
    if (!isSilent) {
      showToast("Could not load dashboard data from backend: " + err.message, "error");
    }
  }
}

function refreshDashboard() {
  loadDashboardData(currentPeriod, currentStartDate, currentEndDate);
  showToast("Refreshing live Firestore metrics...", "info");
}

function renderKPIs(data) {
  if (!data) return;

  const kpiData = data.kpi || {};

  // 1. Total Sales Card
  const salesEl = document.getElementById("kpiTotalSales");
  if (salesEl) {
    const val = kpiData.total_sales !== undefined 
      ? kpiData.total_sales 
      : (data.total_sales !== undefined ? formatCurrency(data.total_sales) : "₹0");
    salesEl.textContent = val;
  }
  const salesGrowthEl = document.getElementById("kpiSalesGrowth");
  if (salesGrowthEl && kpiData.total_sales_growth) {
    salesGrowthEl.textContent = kpiData.total_sales_growth.replace("↑ ", "");
  }
  const salesSubEl = document.getElementById("kpiSalesSub");
  if (salesSubEl && kpiData.total_sales_sub) {
    salesSubEl.textContent = kpiData.total_sales_sub;
  }

  // 2. Total Products Card
  const prodEl = document.getElementById("kpiTotalProducts");
  if (prodEl) {
    const val = kpiData.total_products !== undefined 
      ? kpiData.total_products 
      : (data.total_products !== undefined ? Number(data.total_products).toLocaleString() : "0");
    prodEl.textContent = val;
  }
  const prodGrowthEl = document.getElementById("kpiProductsGrowth");
  if (prodGrowthEl && kpiData.total_products_growth) {
    prodGrowthEl.textContent = kpiData.total_products_growth.replace("↑ ", "");
  }
  const prodSubEl = document.getElementById("kpiProductsSub");
  if (prodSubEl && kpiData.total_products_sub) {
    prodSubEl.textContent = kpiData.total_products_sub;
  }

  // 3. Total Stock Card
  const stockEl = document.getElementById("kpiTotalStock");
  if (stockEl) {
    const val = kpiData.total_stock !== undefined 
      ? kpiData.total_stock 
      : (data.total_stock !== undefined ? Number(data.total_stock).toLocaleString() : "0");
    stockEl.textContent = val;
  }
  const stockGrowthEl = document.getElementById("kpiStockGrowth");
  if (stockGrowthEl && kpiData.total_stock_growth) {
    stockGrowthEl.textContent = kpiData.total_stock_growth.replace("↑ ", "");
  }
  const stockSubEl = document.getElementById("kpiStockSub");
  if (stockSubEl && kpiData.total_stock_sub) {
    stockSubEl.textContent = kpiData.total_stock_sub;
  }

  // 4. Low Stock Items Card
  const lowEl = document.getElementById("kpiLowStock");
  if (lowEl) {
    const val = kpiData.low_stock_items !== undefined 
      ? kpiData.low_stock_items 
      : (data.low_stock_items !== undefined ? data.low_stock_items : 0);
    lowEl.textContent = val;
  }
  const lowGrowthEl = document.getElementById("kpiLowStockGrowth");
  if (lowGrowthEl && kpiData.low_stock_growth) {
    lowGrowthEl.textContent = kpiData.low_stock_growth;
  }
  const lowSubEl = document.getElementById("kpiLowStockSub");
  if (lowSubEl && kpiData.low_stock_sub) {
    lowSubEl.textContent = kpiData.low_stock_sub;
  }

  // Update Dynamic Sparklines based on period
  updateSparklines(data.date_range?.period || "monthly");
}

function updateSparklines(period) {
  const sPath = document.getElementById("kpiSalesSparkline");
  const pPath = document.getElementById("kpiProductsSparkline");
  const stPath = document.getElementById("kpiStockSparkline");
  const lPath = document.getElementById("kpiLowStockSparkline");

  if (period === "daily" || period === "day") {
    if (sPath) sPath.setAttribute("d", "M2 24 L14 20 L28 14 L42 18 L58 6");
    if (pPath) pPath.setAttribute("d", "M2 22 L16 22 L30 18 L44 14 L58 10");
    if (stPath) stPath.setAttribute("d", "M2 18 L15 15 L32 20 L44 10 L58 4");
    if (lPath) lPath.setAttribute("d", "M2 12 L16 16 L30 14 L44 20 L58 22");
  } else if (period === "weekly" || period === "week") {
    if (sPath) sPath.setAttribute("d", "M2 20 L15 15 L28 18 L42 10 L58 5");
    if (pPath) pPath.setAttribute("d", "M2 22 L16 18 L30 15 L44 12 L58 6");
    if (stPath) stPath.setAttribute("d", "M2 16 L16 14 L32 18 L44 12 L58 6");
    if (lPath) lPath.setAttribute("d", "M2 10 L16 14 L30 16 L44 18 L58 24");
  } else if (period === "yearly" || period === "year") {
    if (sPath) sPath.setAttribute("d", "M2 26 L12 24 L24 20 L36 12 L48 8 L58 3");
    if (pPath) pPath.setAttribute("d", "M2 24 L15 20 L30 16 L44 10 L58 4");
    if (stPath) stPath.setAttribute("d", "M2 25 L16 18 L32 14 L44 8 L58 4");
    if (lPath) lPath.setAttribute("d", "M2 8 L16 12 L30 16 L44 20 L58 25");
  } else {
    // monthly
    if (sPath) sPath.setAttribute("d", "M2 22 L15 17 L28 20 L42 8 L58 4");
    if (pPath) pPath.setAttribute("d", "M2 24 L16 19 L30 21 L44 10 L58 6");
    if (stPath) stPath.setAttribute("d", "M2 20 L16 18 L32 23 L44 12 L58 5");
    if (lPath) lPath.setAttribute("d", "M2 8 L16 14 L30 11 L44 19 L58 24");
  }
}

function renderSalesTrendChart(trendData) {
  const ctx = document.getElementById("salesTrendCanvas");
  if (!ctx || !trendData) return;

  const labels = trendData.labels || [];
  const values = trendData.values || [];

  if (salesTrendChartInstance) {
    salesTrendChartInstance.data.labels = labels;
    salesTrendChartInstance.data.datasets[0].data = values;
    salesTrendChartInstance.update();
    return;
  }

  const context = ctx.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 280);
  gradient.addColorStop(0, "rgba(17, 19, 22, 0.12)");
  gradient.addColorStop(1, "rgba(17, 19, 22, 0.0)");

  salesTrendChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Sales (₹)",
        data: values,
        borderColor: "#111316",
        borderWidth: 2.8,
        pointBackgroundColor: "#111316",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2.5,
        pointRadius: 4.5,
        pointHoverRadius: 7,
        fill: true,
        backgroundColor: gradient,
        tension: 0.35
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111316",
          padding: 10,
          cornerRadius: 12,
          titleFont: { family: "Plus Jakarta Sans", size: 12, weight: "bold" },
          bodyFont: { family: "Plus Jakarta Sans", size: 12, weight: "600" },
          displayColors: false,
          callbacks: {
            label: function(context) {
              return " " + formatCurrency(context.raw);
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false, drawBorder: false },
          ticks: {
            font: { family: "Plus Jakarta Sans", size: 11, weight: "600" },
            color: "#8e97a6"
          }
        },
        y: {
          min: 0,
          ticks: {
            font: { family: "Plus Jakarta Sans", size: 11, weight: "600" },
            color: "#8e97a6",
            callback: function(value) {
              if (value >= 100000) return (value / 100000).toFixed(1) + "L";
              if (value >= 1000) return (value / 1000).toFixed(0) + "K";
              return value;
            }
          },
          grid: {
            color: "#f0f2f5",
            drawBorder: false
          }
        }
      }
    }
  });
}

function renderStockDonutChart(stockStatus) {
  const ctx = document.getElementById("stockDonutCanvas");
  if (!ctx || !stockStatus) return;

  const normalPct = stockStatus.normal_pct !== undefined ? stockStatus.normal_pct : 75;
  const lowPct = stockStatus.low_pct !== undefined ? stockStatus.low_pct : 18;
  const critPct = stockStatus.critical_pct !== undefined ? stockStatus.critical_pct : 7;

  // Update center text and legend numbers
  const centerVal = document.querySelector(".donut-center-value");
  if (centerVal && stockStatus.total_stock) {
    centerVal.textContent = stockStatus.total_stock;
  }

  const legendPcts = document.querySelectorAll(".legend-pct");
  if (legendPcts && legendPcts.length >= 3) {
    legendPcts[0].textContent = `${normalPct}%`;
    legendPcts[1].textContent = `${lowPct}%`;
    legendPcts[2].textContent = `${critPct}%`;
  }

  if (stockDonutChartInstance) {
    stockDonutChartInstance.data.datasets[0].data = [normalPct, lowPct, critPct];
    stockDonutChartInstance.update();
    return;
  }

  stockDonutChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Normal Stock", "Low Stock", "Critical Stock"],
      datasets: [{
        data: [normalPct, lowPct, critPct],
        backgroundColor: ["#111316", "#64748b", "#cbd5e1"],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "75%",
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111316",
          padding: 8,
          cornerRadius: 10,
          bodyFont: { family: "Plus Jakarta Sans", size: 12, weight: "600" },
          callbacks: {
            label: function(context) {
              return ` ${context.label}: ${context.raw}%`;
            }
          }
        }
      }
    }
  });
}

function renderTopCategories(categories) {
  const container = document.querySelector(".category-progress-list");
  if (!container || !categories || !categories.length) return;

  container.innerHTML = categories.slice(0, 4).map((c, idx) => {
    const pct = c.percentage || 0;
    const catName = c.category || "General";
    return `
      <div class="category-progress-item">
        <div class="category-progress-meta">
          <span>${catName}</span>
          <span>${pct}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" style="width: ${pct}%; background: var(--text-main);"></div>
        </div>
      </div>
    `;
  }).join("");
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

function renderRecentSalesTable(sales) {
  const tableBody = document.getElementById("recentSalesTableBody");
  if (!tableBody || !sales) return;

  if (sales.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--text-muted);">No sales transactions yet.</td></tr>`;
    return;
  }

  tableBody.innerHTML = sales.map(s => {
    const isCompleted = String(s.status).toLowerCase() === "completed";
    const badgeClass = isCompleted ? "badge-success" : "badge-warning";
    const cat = s.category_name || s.category || "General";
    const icon = getGarmentIcon(cat);
    const prodName = s.product_name || s.product || "Garment Item";
    const saleId = s.sale_id || s.id || "";
    const saleDate = s.sale_date || s.date || "";
    const amountFormatted = s.total_formatted || formatCurrency(s.total_amount || s.total || 0);

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-muted);">${saleId}</td>
        <td>
          <div class="table-product-cell">
            <div class="garment-avatar">
              <i class="fa-solid ${icon}"></i>
            </div>
            <span style="font-weight: 700;">${prodName}</span>
          </div>
        </td>
        <td><span style="color: var(--text-muted); font-weight: 600;">${cat}</span></td>
        <td style="font-weight: 700;">${s.quantity} pcs</td>
        <td style="font-weight: 800; color: var(--text-main);">${amountFormatted}</td>
        <td style="color: var(--text-muted); font-weight: 500;">${saleDate}</td>
        <td>
          <span class="badge ${badgeClass}">${s.status}</span>
        </td>
        <td>
          <button class="table-action-dots" onclick="showToast('Sale ${saleId} verified', 'info')" title="Options">
            <i class="fa-solid fa-ellipsis-vertical"></i>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}
