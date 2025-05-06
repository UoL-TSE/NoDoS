import { fetchAPI } from "./fetch.js";

const params = new URLSearchParams(window.location.search);
const proxyId = params.get('proxy_id');
const configId = params.get('config_id');
document.getElementById("proxy-label").innerText = proxyId
    ? `Monitoring Proxy Config ID: ${proxyId}`
    : "Monitoring Local Proxy";

const removeIP = (ip, list) => {
    if (!confirm(`Are you sure you want to remove ${ip} from the ${list}?`))
        return;

    window.removeFromList(ip, list);
}


const renderList = (list_id, list) => {
    const container = document.getElementById(list_id);
    container.innerHTML = '';
    list.forEach(ip => {
        const li = document.createElement('li');
        li.textContent = ip;
        li.onclick = () => {
            removeIP(ip, list_id);
        }
        container.appendChild(li);
    });
};

const fetchIPData = async (forever=false) => {
    try {
        const response = await fetchAPI("GET", `/config/${configId}/all-lists`);
        const data = await response.json();
        renderList('whitelist', data.whitelist.ips || []);
        renderList('blacklist', data.blacklist.ips || []);
    } catch (error) {
        console.error('Error fetching IP data:', error);
    } finally {
        if (forever) {
            await new Promise(t => setTimeout(t, 1000));
            fetchIPData(true);
        }
    }
};

window.addToList = async (list) => {
    const ip = document.getElementById('ip-input').value.trim();
    if (!ip) return;

    try {
        const response = await fetchAPI("PUT", `/config/${configId}/${list}`, JSON.stringify({ ip: ip }));
    } catch (error) {
        console.error('Error modifying IP:', error);
    }
    
    await fetchIPData();
};

window.removeFromList = async (ip, list) => {
    try {
        const response = await fetchAPI("DELETE", `/config/${configId}/${list}`, JSON.stringify({ ip: ip }));
    } catch (error) {
        console.error('Error modifying IP:', error);
    }
    
    await fetchIPData();
};


fetchIPData(true);
