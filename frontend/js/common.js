/**
 * FABRICFLOW ANALYTICS - COMMON JAVASCRIPT & SHARED STORE
 * Garment Inventory Management System
 * Production Flask REST API Client with Offline LocalStorage Fallback
 */

// Central API Base URL Configuration (Configurable for local and production deployment)
const API_BASE_URL = window.location.origin.includes(":5000") 
  ? `${window.location.origin}/api` 
  : "http://127.0.0.1:5000/api";

/**
 * Reusable Central API Request Helper
 * Handles GET, POST, PUT, DELETE, JSON parsing, error throwing, and auth headers.
 */
async function apiRequest(endpoint, method = "GET", data = null, customHeaders = {}) {
  const url = endpoint.startsWith("http") 
    ? endpoint 
    : `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
  
  const token = localStorage.getItem("fabricflow_token") || "fabricflow2024";

  const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
    ...customHeaders
  };

  const options = {
    method: method.toUpperCase(),
    headers
  };

  if (data && ["POST", "PUT", "PATCH"].includes(options.method)) {
    options.body = typeof data === "string" ? data : JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    const result = await response.json().catch(() => ({}));

    if (!response.ok || result.success === false) {
      const errorMsg = result.message || (result.errors && result.errors[0]) || `API Error: ${response.status} ${response.statusText}`;
      throw new Error(errorMsg);
    }

    return result;
  } catch (err) {
    console.error(`[FabricFlow API Request Failed] ${method} ${endpoint}:`, err.message);
    throw err;
  }
}

/**
 * Backwards compatible alias for existing components
 */
async function apiFetch(endpoint, options = {}) {
  const method = options.method || "GET";
  let data = null;
  if (options.body) {
    try {
      data = typeof options.body === "string" ? JSON.parse(options.body) : options.body;
    } catch (e) {
      data = options.body;
    }
  }
  return await apiRequest(endpoint, method, data, options.headers || {});
}

// Initial Fallback Mock Dataset for FabricFlow Analytics
const DEFAULT_PRODUCTS = [
  { id: "P001", name: "Classic Cotton T-Shirt", category: "Casual", size: "M", price: 899, supplier: "ABC Textiles", stock: 120, status: "Normal", minStock: 25 },
  { id: "P002", name: "Slim Fit Denim Jeans", category: "Denim", size: "32", price: 1999, supplier: "Vogue Fabrics", stock: 10, status: "Low", minStock: 20 },
  { id: "P003", name: "Oxford Formal Shirt", category: "Formal", size: "L", price: 1499, supplier: "Prime Weaves", stock: 85, status: "Normal", minStock: 15 },
  { id: "P004", name: "Quilted Winter Jacket", category: "Outerwear", size: "XL", price: 3499, supplier: "Apex Garments", stock: 4, status: "Critical", minStock: 12 },
  { id: "P005", name: "Oversized Graphic Tee", category: "Casual", size: "L", price: 1099, supplier: "ABC Textiles", stock: 140, status: "Normal", minStock: 30 },
  { id: "P006", name: "Linen Casual Trousers", category: "Casual", size: "34", price: 1899, supplier: "Heritage Looms", stock: 45, status: "Normal", minStock: 15 },
  { id: "P007", name: "Flannel Plaid Shirt", category: "Formal", size: "M", price: 1599, supplier: "Prime Weaves", stock: 8, status: "Low", minStock: 18 },
  { id: "P008", name: "Fleece Hooded Sweatshirt", category: "Outerwear", size: "L", price: 2199, supplier: "Apex Garments", stock: 65, status: "Normal", minStock: 20 },
  { id: "P009", name: "Ripped Skinny Jeans", category: "Denim", size: "30", price: 2299, supplier: "Vogue Fabrics", stock: 3, status: "Critical", minStock: 15 },
  { id: "P010", name: "Polo Collar T-Shirt", category: "Casual", size: "M", price: 1199, supplier: "ABC Textiles", stock: 95, status: "Normal", minStock: 25 },
  { id: "P011", name: "Silk Blend Party Dress Shirt", category: "Formal", size: "S", price: 2499, supplier: "Heritage Looms", stock: 32, status: "Normal", minStock: 10 },
  { id: "P012", name: "Bomber Windbreaker Jacket", category: "Outerwear", size: "M", price: 2899, supplier: "Apex Garments", stock: 14, status: "Low", minStock: 15 }
];

const DEFAULT_SALES = [
  { id: "S001", product: "Classic Cotton T-Shirt", category: "Casual", quantity: 20, unitPrice: 899, total: 17980, date: "2024-09-01", status: "Completed" },
  { id: "S002", product: "Slim Fit Denim Jeans", category: "Denim", quantity: 10, unitPrice: 1299, total: 12990, date: "2024-09-02", status: "Completed" },
  { id: "S003", product: "Oxford Formal Shirt", category: "Formal", quantity: 15, unitPrice: 899, total: 13485, date: "2024-09-03", status: "Completed" },
  { id: "S004", product: "Quilted Winter Jacket", category: "Outerwear", quantity: 5, unitPrice: 1799, total: 8995, date: "2024-09-04", status: "Completed" },
  { id: "S005", product: "Oversized Graphic Tee", category: "Casual", quantity: 30, unitPrice: 849, total: 25470, date: "2024-09-05", status: "Pending" },
  { id: "S006", product: "Linen Casual Trousers", category: "Casual", quantity: 12, unitPrice: 1899, total: 22788, date: "2024-09-06", status: "Completed" },
  { id: "S007", product: "Fleece Hooded Sweatshirt", category: "Outerwear", quantity: 8, unitPrice: 2199, total: 17592, date: "2024-09-07", status: "Completed" },
  { id: "S008", product: "Polo Collar T-Shirt", category: "Casual", quantity: 25, unitPrice: 1199, total: 29975, date: "2024-09-08", status: "Completed" },
  { id: "S009", product: "Flannel Plaid Shirt", category: "Formal", quantity: 6, unitPrice: 1599, total: 9594, date: "2024-09-09", status: "Pending" },
  { id: "S010", product: "Silk Blend Party Dress Shirt", category: "Formal", quantity: 14, unitPrice: 2499, total: 34986, date: "2024-09-10", status: "Completed" }
];

const DEFAULT_SUPPLIERS = [
  { id: "SUP-101", name: "ABC Textiles Co.", contact: "+91 98765 43210", email: "orders@abctextiles.com", address: "Surat Textile Hub, Gujarat", productsSupplied: 18, status: "Active" },
  { id: "SUP-102", name: "Vogue Fabrics Mill", contact: "+91 98111 22334", email: "info@voguefabrics.in", address: "Tirupur Apparel Park, Tamil Nadu", productsSupplied: 12, status: "Active" },
  { id: "SUP-103", name: "Prime Weaves Ltd.", contact: "+91 97234 56789", email: "sales@primeweaves.com", address: "Bhiwandi Industrial Estate, Maharashtra", productsSupplied: 15, status: "Active" },
  { id: "SUP-104", name: "Apex Garments Supply", contact: "+91 99444 88776", email: "contact@apexgarments.com", address: "Ludhiana Woolen Park, Punjab", productsSupplied: 9, status: "Active" },
  { id: "SUP-105", name: "Heritage Looms & Threads", contact: "+91 98333 11223", email: "support@heritagelooms.com", address: "Varanasi Silk Cluster, UP", productsSupplied: 6, status: "Under Review" }
];

// Data Store Layer
class FabricFlowStore {
  constructor() {
    this.init();
  }

  init() {
    if (!localStorage.getItem("fabricflow_products")) {
      localStorage.setItem("fabricflow_products", JSON.stringify(DEFAULT_PRODUCTS));
    }
    if (!localStorage.getItem("fabricflow_sales")) {
      localStorage.setItem("fabricflow_sales", JSON.stringify(DEFAULT_SALES));
    }
    if (!localStorage.getItem("fabricflow_suppliers")) {
      localStorage.setItem("fabricflow_suppliers", JSON.stringify(DEFAULT_SUPPLIERS));
    }
  }

  getProducts() {
    return JSON.parse(localStorage.getItem("fabricflow_products") || "[]");
  }

  saveProducts(products) {
    localStorage.setItem("fabricflow_products", JSON.stringify(products));
  }

  getSales() {
    return JSON.parse(localStorage.getItem("fabricflow_sales") || "[]");
  }

  saveSales(sales) {
    localStorage.setItem("fabricflow_sales", JSON.stringify(sales));
  }

  getSuppliers() {
    return JSON.parse(localStorage.getItem("fabricflow_suppliers") || "[]");
  }

  saveSuppliers(suppliers) {
    localStorage.setItem("fabricflow_suppliers", JSON.stringify(suppliers));
  }
}

const dataStore = new FabricFlowStore();

// Utility Functions
function formatCurrency(num) {
  return "₹" + Number(num).toLocaleString("en-IN");
}

function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  const icon = type === "success" ? "fa-circle-check text-success" : (type === "error" ? "fa-circle-exclamation text-danger" : "fa-triangle-exclamation text-warning");
  
  toast.innerHTML = `
    <i class="fa-solid ${icon}"></i>
    <div style="flex: 1; font-size: 0.88rem; font-weight: 600;">${message}</div>
    <button style="background:none;border:none;color:var(--text-light);cursor:pointer;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
    document.body.style.overflow = "";
  }
}

// Global UI Setup
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("fabricflow_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);

  // Mobile menu toggle
  const mobileBtn = document.getElementById("mobileMenuBtn");
  const sidebar = document.querySelector(".sidebar");
  let overlay = document.querySelector(".sidebar-overlay");

  if (!overlay && sidebar) {
    overlay = document.createElement("div");
    overlay.className = "sidebar-overlay";
    document.body.appendChild(overlay);
  }

  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
      if (overlay) overlay.classList.toggle("active");
    });
  }

  if (overlay) {
    overlay.addEventListener("click", () => {
      if (sidebar) sidebar.classList.remove("mobile-open");
      overlay.classList.remove("active");
    });
  }

  // Analytics dropdown menu in sidebar
  const analyticsToggle = document.getElementById("analyticsToggle");
  if (analyticsToggle) {
    analyticsToggle.addEventListener("click", (e) => {
      e.preventDefault();
      const parent = analyticsToggle.closest(".nav-item");
      if (parent) parent.classList.toggle("open");
    });
  }

  // User Profile dropdown
  const profileBtn = document.getElementById("userProfileBtn");
  const profileMenu = document.getElementById("userProfileDropdown");
  if (profileBtn && profileMenu) {
    profileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      profileMenu.classList.toggle("show");
    });

    document.addEventListener("click", () => {
      profileMenu.classList.remove("show");
    });
  }

  // Active link highlighters
  const currentPath = window.location.pathname.split("/").pop() || "dashboard.html";
  const urlParams = new URLSearchParams(window.location.search);
  const currentTab = urlParams.get("tab") || "sales";

  // Reset active classes first
  document.querySelectorAll(".nav-link.active, .submenu-link.active").forEach(el => {
    el.classList.remove("active");
  });

  // Activate parent nav link
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href") || "";
    if (link.classList.contains("nav-dropdown-toggle")) {
      const parentNav = link.closest(".nav-item");
      if (currentPath.includes("analytics")) {
        link.classList.add("active");
        if (parentNav) parentNav.classList.add("open");
      }
    } else if (href) {
      const linkBase = href.split("?")[0].split("/").pop();
      const currentBase = currentPath.split("?")[0];
      if (linkBase && (linkBase === currentBase || (currentBase === "" && linkBase === "dashboard.html"))) {
        link.classList.add("active");
      }
    }
  });

  // Activate ONLY the single matching submenu link on analytics page
  if (currentPath.includes("analytics")) {
    const submenuLinks = document.querySelectorAll(".submenu-link");
    let matched = false;
    submenuLinks.forEach(link => {
      const href = link.getAttribute("href") || "";
      if (href.includes(`tab=${currentTab}`)) {
        link.classList.add("active");
        matched = true;
      }
    });
    if (!matched && submenuLinks.length > 0) {
      submenuLinks[0].classList.add("active");
    }
  }

  // Global search
  const globalSearchInput = document.getElementById("globalSearchInput");
  if (globalSearchInput) {
    globalSearchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && globalSearchInput.value.trim()) {
        showToast(`Searching for "${globalSearchInput.value.trim()}"...`, "info");
      }
    });
  }
});
