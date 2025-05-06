import { fetchAPI } from "./fetch.js";

async function fetchProxies() {
    try {
        const res = await fetchAPI("GET", "/proxy/all");
        if (res.status === 404) {
            document.getElementById("error-message").innerText = "No proxies found";
            return;
        }

        if (res.status !== 200) {
            throw res.json();
        }

        const proxies = (await res.json())["proxies"];
        renderProxies(proxies);
    } catch (error) {
        console.error("Failed to fetch proxy data:", error);
        document.getElementById("error-message").innerText = "Error loading proxies";
    }
}

function renderProxies(proxies) {
    const container = document.getElementById("proxy-list");
    container.innerHTML = '';
    proxies.forEach(proxy => {
        const div = document.createElement("div");
        div.className = "bg-white p-6 rounded-lg shadow";
        div.innerHTML = `
          <h2 class="text-xl font-semibold text-gray-800">${proxy.config.name}</h2>
          <p class="text-gray-500 text-sm mb-3">${proxy.config.proxy_host}:${proxy.config.proxy_port}</p>
          <p class="text-gray-500 text-sm mb-3">${proxy.config.real_host}:${proxy.config.real_port}</p>
          <a href="./monitor.html?config_id=${proxy.config_id}&proxy_id=${proxy.proxy_id}"
             class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" target="_blank">
            View Monitor
          </a>
        `;
        container.appendChild(div);
    });
}

fetchProxies();
