import { fetchAPI } from "./fetch.js";

async function fetchProxies(forever=false) {
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
        document.getElementById("error-message").innerText = "";
        renderProxies(proxies);
    } catch (error) {
        console.error("Failed to fetch proxy data:", error);
        document.getElementById("error-message").innerText = "Error loading proxies";
    } finally {
        if (forever) {
            await new Promise(t => setTimeout(t, 1000));
            fetchProxies(true).then();
        }
    }
}

function renderProxies(proxies) {
    const container = document.getElementById("proxy-list");
    container.innerHTML = '';
    proxies.forEach(proxy => {
        const divClass = proxy.running ? "running" : "stopped";
        const div = document.createElement("div");
        div.id = `proxy-${proxy.proxy_id}`;
        div.className = `bg-white p-6 rounded-lg shadow proxy-panel ${divClass}`;
        div.innerHTML = `
          <h2 class="text-xl font-semibold text-gray-800">${proxy.config.name}</h2>
          <p class="text-gray-500 text-sm mb-3">${proxy.config.proxy_host}:${proxy.config.proxy_port}</p>
          <p class="text-gray-500 text-sm mb-3">${proxy.config.real_host}:${proxy.config.real_port}</p>
          <div class="grid grid-cols-2 gap-4 w-1/2">
            <a href="./monitor.html?config_id=${proxy.config_id}&proxy_id=${proxy.proxy_id}"
               class="bg-blue-600 text-center text-white px-4 py-2 rounded hover:bg-blue-700" target="_blank">
              View Monitor
            </a>
            <button class="bg-red-600 text-center text-white px-4 py-2 rounded hover:bg-red-700" onclick="window.termProxy(${proxy.proxy_id});">Terminate</button>
          </div>
        `;
        container.appendChild(div);
    });
}

window.termProxy = async (proxyId) => {
    document.getElementById(`proxy-${proxyId}`).remove();

    const resp = await fetchAPI("DELETE", `/proxy/${proxyId}`);
    if (resp.status !== 200) {
        console.error(`Error deleting proxy with id ${proxyId}`);
    }
}

fetchProxies(true);
