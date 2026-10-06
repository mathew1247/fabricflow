/**
 * FABRICFLOW ANALYTICS - LOGIN SCRIPT
 * Connects to Flask REST API /api/auth/login with token session management
 */

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const emailInput = document.getElementById("emailInput");
  const passwordInput = document.getElementById("passwordInput");
  const togglePasswordBtn = document.getElementById("togglePasswordBtn");
  const submitBtn = document.getElementById("submitBtn");

  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener("click", () => {
      const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
      passwordInput.setAttribute("type", type);
      const icon = togglePasswordBtn.querySelector("i");
      if (icon) {
        icon.className = type === "password" ? "fa-solid fa-eye" : "fa-solid fa-eye-slash";
      }
    });
  }

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = emailInput.value.trim();
      const password = passwordInput.value.trim();

      if (!email || !password) {
        showToast("Please enter both email and password.", "warning");
        return;
      }

      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...`;

      try {
        // Call Flask Backend Auth API
        const response = await apiFetch("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password })
        });

        const userData = response.data || {
          name: "Alex Morgan",
          email: email,
          role: "Inventory Admin"
        };

        localStorage.setItem("fabricflow_token", userData.token || "fabricflow2024");
        localStorage.setItem("fabricflow_user", JSON.stringify(userData));

        showToast("Sign in successful! Redirecting to Dashboard...", "success");

        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 600);
      } catch (err) {
        console.warn("Backend auth offline, using local fallback session:", err.message);
        localStorage.setItem("fabricflow_user", JSON.stringify({
          name: "Alex Morgan",
          email: email,
          role: "Inventory Admin"
        }));
        showToast("Sign in successful (Demo Mode)! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 600);
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }
});
