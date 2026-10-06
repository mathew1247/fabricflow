/**
 * FABRICFLOW ANALYTICS - SETTINGS SCRIPT
 * Profile preferences, theme switcher (Light/Dark), and alert settings
 */

document.addEventListener("DOMContentLoaded", () => {
  loadUserSettings();
  setupSettingsListeners();
});

function loadUserSettings() {
  const user = JSON.parse(localStorage.getItem("fabricflow_user") || '{"name":"Alex Morgan","email":"admin@fabricflow.com","role":"Inventory Admin"}');
  
  const nameInput = document.getElementById("profileName");
  const emailInput = document.getElementById("profileEmail");
  const roleInput = document.getElementById("profileRole");

  if (nameInput) nameInput.value = user.name;
  if (emailInput) emailInput.value = user.email;
  if (roleInput) roleInput.value = user.role;

  // Theme check
  const currentTheme = localStorage.getItem("fabricflow_theme") || "light";
  document.querySelectorAll(".theme-card-option").forEach(card => {
    if (card.getAttribute("data-theme-val") === currentTheme) {
      card.classList.add("active");
    } else {
      card.classList.remove("active");
    }
  });
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("fabricflow_theme", theme);

  document.querySelectorAll(".theme-card-option").forEach(card => {
    if (card.getAttribute("data-theme-val") === theme) {
      card.classList.add("active");
    } else {
      card.classList.remove("active");
    }
  });

  showToast(`Theme switched to ${theme === 'dark' ? 'Dark Mode' : 'Light Mode'}.`, "info");
}

function setupSettingsListeners() {
  // Theme options
  document.querySelectorAll(".theme-card-option").forEach(card => {
    card.addEventListener("click", () => {
      const themeVal = card.getAttribute("data-theme-val");
      setTheme(themeVal);
    });
  });

  // Settings form save
  document.getElementById("settingsForm")?.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("profileName").value.trim();
    const email = document.getElementById("profileEmail").value.trim();
    const role = document.getElementById("profileRole").value.trim();

    localStorage.setItem("fabricflow_user", JSON.stringify({ name, email, role }));
    showToast("System settings and preferences saved successfully!", "success");
  });
}
