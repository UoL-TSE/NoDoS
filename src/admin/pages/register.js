document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-form");
    const emailInput = document.getElementById("register-username");
    const passwordInput = document.getElementById("register-password");
    const errorMsg = document.getElementById("register-error");
  
    emailInput.addEventListener("invalid", function (e) {
      e.preventDefault();
      this.setCustomValidity("Email must end with @lincoln.ac.uk or @students.lincoln.ac.uk");
    });
  
    emailInput.addEventListener("input", function () {
      this.setCustomValidity("");
    });
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
  
      const username = emailInput.value.trim();
      const password = passwordInput.value.trim();
  
      try {
        const res = await fetch("/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });
  
        const data = await res.json();
  
        if (!res.ok) {
          errorMsg.textContent = data.detail || "Registration failed";
          errorMsg.classList.remove("hidden");
        } else {
          window.location.href = "login.html";
        }
      } catch (err) {
        errorMsg.textContent = "Network error";
        errorMsg.classList.remove("hidden");
      }
    });
  });
  