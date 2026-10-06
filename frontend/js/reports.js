/**
 * FABRICFLOW ANALYTICS - REPORTS SCRIPT
 * Connects to Flask REST API /api/reports/preview & /api/reports/export/csv
 * Generates and downloads real reports from Cloud Firestore
 */

let currentReportType = "inventory";

document.addEventListener("DOMContentLoaded", () => {
  renderReportPreview(currentReportType);
  setupReportListeners();
});

function selectReport(type) {
  currentReportType = type;
  document.querySelectorAll(".report-card").forEach(card => {
    if (card.getAttribute("data-report") === type) {
      card.classList.add("selected");
    } else {
      card.classList.remove("selected");
    }
  });

  renderReportPreview(type);
  showToast(`Switched preview to ${formatReportName(type)}`, "info");
}

function formatReportName(type) {
  switch (type) {
    case "inventory": return "Inventory Valuation Report";
    case "sales": return "Sales Summary Report";
    case "products": return "Products Catalog Report";
    case "performance": return "Product Performance Report";
    case "lowstock": case "low-stock": return "Low Stock & Risk Report";
    case "forecast": return "Demand Forecast Report";
    default: return "Report";
  }
}

async function renderReportPreview(type) {
  const titleEl = document.getElementById("previewReportTitle");
  const countEl = document.getElementById("previewRowCount");
  const thead = document.getElementById("previewReportThead");
  const tbody = document.getElementById("previewReportTbody");

  if (titleEl) titleEl.textContent = formatReportName(type);
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Generating report from Cloud Firestore...</td></tr>`;
  }

  try {
    const res = await apiRequest(`/reports/preview?type=${type}`);
    const reportData = res.data || {};

    if (thead && reportData.headers) {
      thead.innerHTML = `<tr>${reportData.headers.map(h => `<th>${h}</th>`).join("")}</tr>`;
    }

    if (tbody && reportData.rows) {
      if (reportData.rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--text-muted);">No records found in this report.</td></tr>`;
      } else {
        tbody.innerHTML = reportData.rows.map(row => {
          const values = Object.values(row);
          return `
            <tr>
              ${values.map((v, idx) => {
                if (idx === 0) return `<td style="font-weight:700; color:var(--text-main);">${v}</td>`;
                const vStr = String(v);
                if (vStr.includes("Normal") || vStr.includes("Completed") || vStr.includes("Fast") || vStr.includes("Active")) {
                  return `<td><span class="badge badge-success">${v}</span></td>`;
                }
                if (vStr.includes("Low") || vStr.includes("Pending") || vStr.includes("Slow") || vStr.includes("Reduce") || vStr.includes("Maintain")) {
                  return `<td><span class="badge badge-warning">${v}</span></td>`;
                }
                if (vStr.includes("Critical") || vStr.includes("Increase")) {
                  return `<td><span class="badge badge-danger">${v}</span></td>`;
                }
                return `<td>${v}</td>`;
              }).join("")}
            </tr>
          `;
        }).join("");
      }
    }

    if (countEl) countEl.textContent = `${reportData.count || 0} records`;
  } catch (err) {
    console.error("API report preview failed:", err.message);
    showToast("Failed to preview report: " + err.message, "error");
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Error loading report from server.</td></tr>`;
    }
  }
}

function downloadReportCSV(type = currentReportType) {
  const directApiUrl = `${API_BASE_URL}/reports/${type}?format=csv`;
  
  // Trigger direct download from backend
  const link = document.createElement("a");
  link.href = directApiUrl;
  link.setAttribute("download", `fabricflow_${type}_report_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Downloading real ${formatReportName(type)} CSV from Firestore...`, "success");
}

function setupReportListeners() {
  document.getElementById("downloadCurrentReportBtn")?.addEventListener("click", () => {
    downloadReportCSV(currentReportType);
  });
}
