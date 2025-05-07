import { setToken } from "./fetch.js";

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const errorMsg = document.getElementById("login-error");

  errorMsg.classList.add("hidden");
  errorMsg.textContent = "";

  if (password.length < 8) {
    errorMsg.textContent = "Password must be at least 8 characters long.";
    errorMsg.classList.remove("hidden");
    return;
  }

  try {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    if (!res.ok) {
        // ✅ Server error handling
        if (typeof data.detail === "string") {
          errorMsg.textContent = data.detail;
        } else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
          errorMsg.textContent = data.detail[0].msg;
        } else if (data.detail?.msg) {
          errorMsg.textContent = data.detail.msg;
        } else {
          errorMsg.textContent = "Login failed.";
        }
  
        errorMsg.classList.remove("hidden");
        return;
      }
    // Store token in session
    setToken(data.token);

    // Redirect to dashboard
    window.location.href = "./dashboard.html";

  } catch (err) {
    errorMsg.textContent = "Network error. Please try again.";
    errorMsg.classList.remove("hidden");
  }
});
