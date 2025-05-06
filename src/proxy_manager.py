from multiprocessing import Lock

from models import Config
from proxy.proxy import Proxy


class ProxyNotFound(Exception):
    def __init__(self, proxy_id: int):
        super().__init__(f"Proxy with ID {proxy_id} was not found")


class _ProxyManager:
    proxies_lock = Lock()
    proxies: list[Proxy | None] = []

    def cleanup(self):
        # Terminate proxy servers when this object is deleted
        for proxy in self.proxies:
            if not proxy:
                continue

            proxy.terminate()

    def poll(self):
        for proxy in self.proxies:
            if proxy:
                proxy.poll()

    def get_new_id(self) -> int | None:
        # Either find the first empty spot in the list or return the max
        for i, proxy in enumerate(self.proxies):
            if proxy is None:
                return i

        return None

    async def new(self, user_id: int, config_id: int, config: Config) -> int:
        # Create new process and add it to the list
        with self.proxies_lock:
            proxy_id = self.get_new_id()
            proxy = Proxy(user_id, config_id, config)

            if proxy_id is None:
                self.proxies.append(proxy)
                proxy_id = len(self.proxies) - 1
            else:
                self.proxies[proxy_id] = proxy
        
        return proxy_id

    def terminate(self, proxy_id: int):
        # If the process_id doesn't point to a process, raise ProxyNotFound
        if proxy_id > len(self.proxies)-1 or self.proxies[proxy_id] is None:
            raise ProxyNotFound(proxy_id)
        
        # Get the proxy and assert it's existence as it should exist
        proxy = self.proxies[proxy_id]
        assert proxy

        proxy.terminate()
        self.proxies[proxy_id] = None

    def allproxies(self) -> list[Proxy]:
        # Poll all proxies
        self.poll()

        # Return all proxies
        return [proxy for proxy in self.proxies if proxy]



proxy_manager = _ProxyManager()
