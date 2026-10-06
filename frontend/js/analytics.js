/**
 * FABRICFLOW ANALYTICS - ANALYTICS SCRIPT
 * Production analytics dashboard connected to Flask REST API /api/analytics & Pandas/NumPy
 */

let charts = {
  salesTrend: null,
  salesCategory: null,
  salesTarget: null,
  dailySales: null,
  stockDist: null,
  movement: null,
  categoryStock: null
};

let loadedAnalyticsData = null;

document.addEventListener("DOMContentLoaded", () => {
  setupTabNavigation();
  loadAnalytics();

  const urlParams = new URLSearchParams(window.location.search);
  const requestedTab = urlParams.get("tab");
  if (requestedTab) {
    switchTab(requestedTab);
  }
});

async function loadAnalytics() {
  try {
    const res = await apiRequest("/analytics");
    loadedAnalyticsData = res.data || {};

    if (loadedAnalyticsData.sales) {
      renderSalesCharts(loadedAnalyticsData.sales);
    }
    if (loadedAnalyticsData.inventory) {
      renderInventoryCharts(loadedAnalyticsData.inventory);
    }
    if (loadedAnalyticsData.performance) {
      renderPerformanceTables(loadedAnalyticsData.performance);
    } else if (loadedAnalyticsData.products) {
      renderPerformanceTables(loadedAnalyticsData.products);
    }
  } catch (err) {
    console.error("API analytics failed:", err.message);
    showToast("Failed to load analytics: " + err.message, "error");
  }
}

function setupTabNavigation() {
  const tabBtns = document.querySelectorAll(".analytics-tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const tabKey = btn.getAttribute("data-tab");
      switchTab(tabKey);
    });
  });
}

function switchTab(tabKey) {
  const tabBtns = document.querySelectorAll(".analytics-tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(b => {
    if (b.getAttribute("data-tab") === tabKey) b.classList.add("active");
    else b.classList.remove("active");
  });

  tabPanes.forEach(pane => {
    if (pane.id === `tab-${tabKey}`) pane.classList.add("active");
    else pane.classList.remove("active");
  });

  // Keep sidebar submenu synchronized with current active tab
  document.querySelectorAll(".submenu-link").forEach(link => {
    const href = link.getAttribute("href") || "";
    if (href.includes(`tab=${tabKey}`)) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

function renderSalesCharts(salesData) {
  // 1. Sales Trend
  const ctx1 = document.getElementById("analyticsSalesTrend");
  if (ctx1 && salesData.sales_by_month) {
    const mData = salesData.sales_by_month;
    if (charts.salesTrend) {
      charts.salesTrend.data.labels = mData.labels;
      charts.salesTrend.data.datasets[0].data = mData.values;
      charts.salesTrend.update();
    } else {
      charts.salesTrend = new Chart(ctx1, {
        type: "line",
        data: {
          labels: mData.labels,
          datasets: [{
            label: "Sales Revenue (₹)",
            data: mData.values,
            borderColor: "#111316",
            backgroundColor: "rgba(17, 19, 22, 0.08)",
            fill: true,
            tension: 0.35,
            borderWidth: 2.8,
            pointRadius: 4,
            pointBackgroundColor: "#111316"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: "#111316",
              padding: 8,
              cornerRadius: 10,
              bodyFont: { family: "Plus Jakarta Sans", size: 12, weight: "600" },
              callbacks: {
                label: function(context) { return " " + formatCurrency(context.raw); }
              }
            }
          },
          scales: {
            y: { grid: { color: "#f0f2f5" }, ticks: { font: { family: "Plus Jakarta Sans", weight: "600" } } },
            x: { grid: { display: false }, ticks: { font: { family: "Plus Jakarta Sans", weight: "600" } } }
          }
        }
      });
    }
  }

  // 2. Sales by Category
  const ctx2 = document.getElementById("salesByCategoryChart");
  if (ctx2 && salesData.sales_by_category) {
    const catData = salesData.sales_by_category;
    const labels = catData.map(c => c.category);
    const revenues = catData.map(c => c.revenue);
    const colors = ["#111316", "#475569", "#64748b", "#94a3b8", "#cbd5e1", "#e2e8f0"];

    if (charts.salesCategory) {
      charts.salesCategory.data.labels = labels;
      charts.salesCategory.data.datasets[0].data = revenues;
      charts.salesCategory.update();
    } else {
      charts.salesCategory = new Chart(ctx2, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Revenue (₹)",
            data: revenues,
            backgroundColor: colors.slice(0, labels.length),
            borderRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: "#111316",
              padding: 8,
              cornerRadius: 10,
              callbacks: {
                label: function(context) { return " " + formatCurrency(context.raw); }
              }
            }
          },
          scales: {
            y: { grid: { color: "#f0f2f5" } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  }

  // 3. Monthly Sales vs Target
  const ctx3 = document.getElementById("monthlySalesTargetChart");
  if (ctx3 && salesData.monthly_targets) {
    const tData = salesData.monthly_targets;
    if (charts.salesTarget) {
      charts.salesTarget.data.labels = tData.labels;
      charts.salesTarget.data.datasets[0].data = tData.actual;
      charts.salesTarget.data.datasets[1].data = tData.target;
      charts.salesTarget.update();
    } else {
      charts.salesTarget = new Chart(ctx3, {
        type: "bar",
        data: {
          labels: tData.labels,
          datasets: [
            {
              label: "Actual Sales (₹)",
              data: tData.actual,
              backgroundColor: "#111316",
              borderRadius: 8,
              barPercentage: 0.6
            },
            {
              label: "Monthly Target (₹)",
              data: tData.target,
              backgroundColor: "#e2e5ea",
              borderRadius: 8,
              barPercentage: 0.6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "top", labels: { font: { family: "Plus Jakarta Sans", weight: "700" } } },
            tooltip: {
              backgroundColor: "#111316",
              cornerRadius: 10,
              callbacks: {
                label: function(context) { return ` ${context.dataset.label}: ${formatCurrency(context.raw)}`; }
              }
            }
          },
          scales: {
            y: { grid: { color: "#f0f2f5" } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  }

  // 4. Daily Sales
  const ctx4 = document.getElementById("dailySalesChart");
  if (ctx4 && salesData.sales_by_day) {
    const dData = salesData.sales_by_day;
    if (charts.dailySales) {
      charts.dailySales.data.labels = dData.labels;
      charts.dailySales.data.datasets[0].data = dData.units;
      charts.dailySales.update();
    } else {
      charts.dailySales = new Chart(ctx4, {
        type: "bar",
        data: {
          labels: dData.labels,
          datasets: [{
            label: "Units Sold",
            data: dData.units,
            backgroundColor: "#111316",
            borderRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: "#111316",
              cornerRadius: 10,
              callbacks: {
                label: function(context) { return ` ${context.raw} units`; }
              }
            }
          },
          scales: {
            y: { grid: { color: "#f0f2f5" } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  }
}

function renderInventoryCharts(invData) {
  // 1. Stock Distribution Doughnut
  const ctx1 = document.getElementById("stockDistChart");
  if (ctx1 && invData.stock_by_category) {
    const dist = invData.stock_by_category;
    const colors = ["#111316", "#475569", "#64748b", "#94a3b8", "#cbd5e1"];

    if (charts.stockDist) {
      charts.stockDist.data.labels = dist.labels;
      charts.stockDist.data.datasets[0].data = dist.percentages;
      charts.stockDist.update();
    } else {
      charts.stockDist = new Chart(ctx1, {
        type: "doughnut",
        data: {
          labels: dist.labels,
          datasets: [{
            data: dist.percentages,
            backgroundColor: colors.slice(0, dist.labels.length),
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "70%",
          plugins: {
            legend: { position: "right", labels: { font: { family: "Plus Jakarta Sans", weight: "600" } } },
            tooltip: {
              backgroundColor: "#111316",
              callbacks: {
                label: function(context) { return ` ${context.label}: ${context.raw}%`; }
              }
            }
          }
        }
      });
    }
  }

  // 2. Inventory Movement
  const ctx2 = document.getElementById("inventoryMovementChart");
  if (ctx2 && invData.inventory_movement) {
    const mv = invData.inventory_movement;
    if (charts.movement) {
      charts.movement.data.labels = mv.labels;
      charts.movement.data.datasets[0].data = mv.inflow;
      charts.movement.data.datasets[1].data = mv.outflow;
      charts.movement.update();
    } else {
      charts.movement = new Chart(ctx2, {
        type: "line",
        data: {
          labels: mv.labels,
          datasets: [
            {
              label: "Inflow (Procured Units)",
              data: mv.inflow,
              borderColor: "#111316",
              backgroundColor: "rgba(17, 19, 22, 0.08)",
              fill: true,
              tension: 0.3,
              borderWidth: 2.5
            },
            {
              label: "Outflow (Sold Units)",
              data: mv.outflow,
              borderColor: "#94a3b8",
              borderDash: [5, 5],
              fill: false,
              tension: 0.3,
              borderWidth: 2.5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "top", labels: { font: { family: "Plus Jakarta Sans", weight: "700" } } } },
          scales: {
            y: { grid: { color: "#f0f2f5" } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  }

  // 3. Category Stock Bar Chart
  const ctx3 = document.getElementById("categoryStockBarChart");
  if (ctx3 && invData.stock_by_category) {
    const dist = invData.stock_by_category;
    if (charts.categoryStock) {
      charts.categoryStock.data.labels = dist.labels;
      charts.categoryStock.data.datasets[0].data = dist.units;
      charts.categoryStock.update();
    } else {
      charts.categoryStock = new Chart(ctx3, {
        type: "bar",
        indexAxis: "y",
        data: {
          labels: dist.labels,
          datasets: [{
            label: "In-Stock Units",
            data: dist.units,
            backgroundColor: "#111316",
            borderRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: "#f0f2f5" } },
            y: { grid: { display: false } }
          }
        }
      });
    }
  }
}

function renderPerformanceTables(perf) {
  const fastBody = document.getElementById("fastMovingTableBody");
  const slowBody = document.getElementById("slowMovingTableBody");

  const fastItems = perf.fast_moving_products || perf.fast_moving || [];
  const slowItems = perf.slow_moving_products || perf.slow_moving || [];

  if (fastBody) {
    if (fastItems.length === 0) {
      fastBody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:1.5rem;color:var(--text-muted);">No fast-moving items detected yet.</td></tr>`;
    } else {
      fastBody.innerHTML = fastItems.map(p => {
        const pname = p.product_name || p.name;
        const pcat = p.category_name || p.category;
        const sold = p.quantity_sold !== undefined ? p.quantity_sold : p.sold;
        const salesVal = p.sales_val_formatted || formatCurrency(p.revenue || p.sales_val || 0);
        const velocity = p.sales_velocity !== undefined ? `${p.sales_velocity} /day` : "";
        return `
          <tr>
            <td>
              <strong>${pname}</strong><br>
              <span style="font-size:0.75rem; color:var(--text-muted);">${pcat} &bull; Vel: ${velocity}</span>
            </td>
            <td style="font-weight:700;">${sold} pcs</td>
            <td style="font-weight:800; color:var(--text-main);">${salesVal}</td>
            <td style="font-weight:600;">${p.stock} units</td>
            <td><span class="badge badge-success">${p.status || 'Fast Moving'}</span></td>
          </tr>
        `;
      }).join("");
    }
  }

  if (slowBody) {
    if (slowItems.length === 0) {
      slowBody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:1.5rem;color:var(--text-muted);">No slow-moving items detected.</td></tr>`;
    } else {
      slowBody.innerHTML = slowItems.map(p => {
        const pname = p.product_name || p.name;
        const pcat = p.category_name || p.category;
        const sold = p.quantity_sold !== undefined ? p.quantity_sold : p.sold;
        const salesVal = p.sales_val_formatted || formatCurrency(p.revenue || p.sales_val || 0);
        const velocity = p.sales_velocity !== undefined ? `${p.sales_velocity} /day` : "";
        return `
          <tr>
            <td>
              <strong>${pname}</strong><br>
              <span style="font-size:0.75rem; color:var(--text-muted);">${pcat} &bull; Vel: ${velocity}</span>
            </td>
            <td style="font-weight:700;">${sold} pcs</td>
            <td style="font-weight:800; color:var(--text-main);">${salesVal}</td>
            <td style="font-weight:600;">${p.stock} units</td>
            <td><span class="badge badge-warning">${p.status || 'Slow Moving'}</span></td>
          </tr>
        `;
      }).join("");
    }
  }
}
