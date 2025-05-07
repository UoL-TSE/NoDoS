import { setToken } from "./fetch.js";

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const errorMsg = document.getElementById("login-error");

  errorMsg.classList.add("hidden");
  errorMsg.textContent = "";

  try {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      errorMsg.textContent = data.detail || "Login failed";
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
